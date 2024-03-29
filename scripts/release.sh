#!/bin/sh

set -eu
set -o pipefail

cd "$(dirname "$0")/.."

latest_version() {
    grep -F -n '## [' "$1" | grep -E -o '[0-9]+\.[0-9]+\.[0-9]+' | head -1
}

new_version() {
    latest=$(latest_version CHANGELOG.md)

    unreleased_changes=$(sed -n '/## \[Unreleased/,/^## /p' CHANGELOG.md)

    if echo "$unreleased_changes" | grep -F -q '### Added'; then
        echo "$latest" | awk -F . '{ print $1 "." ($2 + 1) ".0" }'
        return
    fi
    if echo "$unreleased_changes" | grep -F -q '### Fixed'; then
        echo "$latest" | awk -F . '{ print $1 "." $2 "." ($3 + 1) }'
        return
    fi
    echo "$latest"
}

main() {
    latest=$(latest_version CHANGELOG.md)
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
    sed -e 's/VERSION = .*/VERSION = "'"$v"'"/' -i '' setup.py

    if [ "$(git rev-parse HEAD)" != "$(git rev-parse master)" ]; then
        echo "not on master"
        exit 1
    fi

    if ! git rev-parse v"$v" 2>/dev/null; then
        echo "$v doesn't exist yet"
        git add CHANGELOG.md setup.py
        git commit -m "version $v"
        git tag v"$v"
        echo "you need to: git push && git push --tags"
    fi
}

if [ "$(basename "$0")" = "release.sh" ]; then
    main
fi
