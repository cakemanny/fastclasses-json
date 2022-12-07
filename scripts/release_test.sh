#!/bin/sh

set -eu
set -o pipefail

. scripts/release.sh

RED=$(tput setaf 1)
RST=$(tput sgr0)

assert_equal() {
    if [ "$1" != "$2" ]; then
        {
            echo "${RED}== ASSERTION FAILED ==${RST}"
            echo "expected: '$2'"
            echo "  actual: '$1'"
        } 2>&1
        exit 1
    fi
}

test_latest_version__single_digits () {

    actual=$(echo "
## [0.9.1] - 2022-11-26
" | {
        latest_version /dev/stdin
    })

    expected="0.9.1"
    assert_equal "$actual" "$expected"
}

test_latest_version__double_digits () {

    actual=$(echo "
## [0.10.1] - 2022-11-27
## [0.9.1] - 2022-11-26
" | {
        latest_version /dev/stdin
    })

    expected="0.10.1"
    assert_equal "$actual" "$expected"
}


run_tests() {
    test_latest_version__single_digits
    test_latest_version__double_digits
}

if [ "$(basename "$0")" = "release_test.sh" ]; then
    run_tests
fi
