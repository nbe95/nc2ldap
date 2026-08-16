module.exports = {
  $schema: "https://docs.renovatebot.com/renovate-schema.json",
  extends: [
    "config:recommended",
    "group:all"
  ],
  dependencyDashboard: false,
  assignees: ["nbe95"],
  labels: ["patch"],
  packageRules: [
    {
      // Only patch updates for Python Docker images
      matchDatasources: ["docker"],
      matchPackagePatterns: ["python"],
      matchUpdateTypes: ["patch"]
    },
    {
      // Auto merge non-breaking changes
      matchUpdateTypes: ["patch", "minor"],
      automerge: true,
      automergeType: "pr"
    }
  ]
}
