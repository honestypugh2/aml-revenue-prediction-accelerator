// Example parameters for the QUICKSTART (public) profile.
// Copy and adjust. Do not commit real values you consider sensitive.
using './main.bicep'

param namePrefix = 'revpred'
param publicNetworkAccess = 'Enabled'
param managedNetworkIsolation = 'Disabled'
param tags = {
  workload: 'revenue-prediction-accelerator'
  data: 'synthetic'
  environment: 'dev'
}
