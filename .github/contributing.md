# Contributing

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

## Pull Request Process

These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to our repos or how we handle your PRs.

1. Ensure any build dependencies or sensitive environment variables are removed before posting your PR.
2. In the PR summary, note the features you're adding or changes to existing interfaces.
3. The versioning scheme we use is [SemVer](http://semver.org/).
4. Please squash-merge commits into your PR -- this keeps our history tidy.
5. We'd appreciate if your PR follows the [Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/) spec.
6. Pull Requests are typically merged once they receive approval from two Frame.io developers.  If you haven't gotten approval, feel free to @mention us or send a reminder.

## Testing

We run tests using [pytest](https://docs.pytest.org/en/stable/).  Tests are admittedly weak in this repo, you can help change that!  One rule we care about: any tests run against actual Frame.io processes (like generating assets) should be accompanied by a teardown or cleanup task.

## Report a Bug

Report bugs to Issues in GitHub.  It's okay to report bugs that may not be specific to this library, i.e. if you find a bug core to the API feel free to report it. Try to include info and context that will help us reproduce the problem.
