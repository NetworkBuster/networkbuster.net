# Test Reports

Automated test reports for NetworkBuster repository.

## Structure

```
test-reports/
├── README.md           # This file
├── branch-summary.json # Summary of all branches
├── cadil/              # Reports for cadil user
│   └── test-results.md
├── ai-gateway/         # AI Gateway tests
├── gpu-stats/          # GPU monitoring tests
└── overlay/            # Real-time overlay tests
```

## Branches

| Branch | Status | Last Updated |
|--------|--------|--------------|
| bigtree | Active | 2024-12-24 |
| main | Production | - |
| DATACENTRAL | Feature | - |
| ci/build-apk | CI | - |
| copilot/* | Copilot | - |

## Running Tests

```bash
npm run test              # All tests
npm run ai:test           # AI provider tests
npm run test:devices      # Device registration tests
```
