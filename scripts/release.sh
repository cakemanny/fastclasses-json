#!/bin/sh

set -eu
set -o pipefail

cd "$(dirname "$0")/.."

latest_version() {
    fgrep -n '## [' CHANGELOG.md | grep -o '[0-9]\.[0-9]\.[0-9]' | head -1
}

new_version() {
    # fgrep -n '## [' CHANGELOG.md | fgrep -v Unreleased | sed 's/\].*//'
    latest=$(latest_version)

    unreleased_changes=$(sed -n '/## \[Unreleased/,/^## /p' CHANGELOG.md)

    if echo "$unreleased_changes" | fgrep -q '### Added'; then
        echo "$latest" | awk -F . '{ print $1 "." ($2 + 1) ".0"}'
        return
    fi
    if echo "$unreleased_changes" | fgrep -q '### Fixed'; then
        echo "$latest" | awk -F . '{ print $1 "." $2 "." ($3 + 1) }'
        return
    fi
    echo "$latest"
}

main() {
    latest=$(latest_version)
    v=$(new_version)
    if [ "$v" != "$latest" ]; then
        new_changelog=$(
            awk -v hdr="## [$v] - $(date +%Y-%m-%d)" '
                { print $0 }
                /## \[Unreleased\]/ {
                    print "";
                    print hdr;
                }
            ' CHANGELOG.md
        )
        echo "$new_changelog" > CHANGELOG.md
    fi
    ./scripts/version_changelog

    # TODO: Adjust for dirtiness
    sed -e 's/VERSION = .*/VERSION = "'$v'"/' -i '' setup.py

    if [ "$(git rev-parse HEAD)" != "$(git rev-parse HEAD)" ]; then
        echo "not on master"
        exit
    fi

    if ! git rev-parse v"$v" 2>/dev/null; then
        echo "$v doesn't exist yet"
        git add CHANGELOG.md setup.py
        git commit -m "version $v"
        git tag v"$v"
        echo "you need to: git push && git push --tags"
    fi
}

main
