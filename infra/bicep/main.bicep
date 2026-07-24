// -----------------------------------------------------------------------------
// Azure Machine Learning workspace + dependencies (Bicep).
//
// Two profiles via `publicNetworkAccess`:
//   - Enabled  (quickstart): public workspace for learning/demos.
//   - Disabled (secure):     firewalled dependencies + managed VNet isolation.
//
// No secrets or resource identifiers are hard-coded. Names are derived from a
// caller-supplied prefix. Review against the official secure-workspace guidance
// before production use.
// -----------------------------------------------------------------------------

@description('Short, lowercase prefix used to derive resource names (3-11 chars).')
@minLength(3)
@maxLength(11)
param namePrefix string = 'revpred'

@description('Azure region for all resources.')
param location string = resourceGroup().location

@description('Workspace public network access. "Enabled" = quickstart, "Disabled" = secure.')
@allowed([
  'Enabled'
  'Disabled'
])
param publicNetworkAccess string = 'Enabled'

@description('Managed VNet isolation mode for the secure profile.')
@allowed([
  'Disabled'
  'AllowInternetOutbound'
  'AllowOnlyApprovedOutbound'
])
param managedNetworkIsolation string = 'Disabled'

@description('Tags applied to all resources.')
param tags object = {
  workload: 'revenue-prediction-accelerator'
  data: 'synthetic'
  environment: 'dev'
}

var suffix = uniqueString(resourceGroup().id, namePrefix)
var storageName = toLower('${namePrefix}st${substring(suffix, 0, 6)}')
var kvName = toLower('${namePrefix}-kv-${substring(suffix, 0, 6)}')
var acrName = toLower('${namePrefix}acr${substring(suffix, 0, 6)}')
var aiName = '${namePrefix}-ai-${substring(suffix, 0, 6)}'
var workspaceName = '${namePrefix}-mlw-${substring(suffix, 0, 6)}'
var isSecure = publicNetworkAccess == 'Disabled'

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    publicNetworkAccess: isSecure ? 'Disabled' : 'Enabled'
    networkAcls: {
      defaultAction: isSecure ? 'Deny' : 'Allow'
      bypass: 'AzureServices'
    }
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: kvName
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    enablePurgeProtection: true
    publicNetworkAccess: isSecure ? 'Disabled' : 'Enabled'
    networkAcls: {
      defaultAction: isSecure ? 'Deny' : 'Allow'
      bypass: 'AzureServices'
    }
  }
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' = {
  name: acrName
  location: location
  tags: tags
  sku: {
    name: isSecure ? 'Premium' : 'Standard'
  }
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: isSecure ? 'Disabled' : 'Enabled'
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: aiName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

resource workspace 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: workspaceName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: 'Revenue Prediction Accelerator (${publicNetworkAccess})'
    description: 'Healthcare net-revenue prediction accelerator workspace. Synthetic data only.'
    storageAccount: storage.id
    keyVault: keyVault.id
    applicationInsights: appInsights.id
    containerRegistry: containerRegistry.id
    publicNetworkAccess: publicNetworkAccess
    managedNetwork: {
      isolationMode: managedNetworkIsolation
    }
  }
}

output workspaceName string = workspace.name
output workspaceId string = workspace.id
output storageAccountName string = storage.name
output keyVaultName string = keyVault.name
output containerRegistryName string = containerRegistry.name
output applicationInsightsName string = appInsights.name
output isSecureProfile bool = isSecure
