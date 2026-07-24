// Example parameters for the SECURE profile (firewalled + managed VNet).
// Pair this with private endpoints and private DNS per the docs before
// production use. Copy and adjust.
using './main.bicep'

param namePrefix = 'revpred'
param publicNetworkAccess = 'Disabled'
param managedNetworkIsolation = 'AllowOnlyApprovedOutbound'
param tags = {
  workload: 'revenue-prediction-accelerator'
  data: 'synthetic'
  environment: 'prod'
}
