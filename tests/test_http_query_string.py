from copy import deepcopy

from pytest import mark, raises

from httpea import HttpQueryString
from httpea.http_query_string import build_dict_from_path, parse_qs


@mark.parametrize(
    "query_string,expected",
    [["a", {"a": 1}], ["a[]", {"a": [1]}], ["a[a]", {"a": {"a": 1}}]],
)
def test_build_dict_from_path(query_string: str, expected: dict) -> None:
    assert build_dict_from_path(query_string, 1) == expected


@mark.parametrize("query_string", ["[a]", "[a[]]", "[a][a]", "[]"])
def test_if_fail_build_dict_from_path(query_string: str) -> None:
    with raises(ValueError):
        build_dict_from_path(query_string, 1)


def test_parse_qs_with_no_value() -> None:
    # when
    result = parse_qs("")

    # then
    assert isinstance(result, dict)
    assert result == {}


def test_parse_qs_with_single_value() -> None:
    # when
    result = parse_qs("simple_example=test_value")

    # then
    assert "simple_example" in result
    assert result["simple_example"] == "test_value"


def test_parse_qs_with_multiple_values() -> None:
    # when
    result = parse_qs("test_1=1&test_2=2&test_3=-3")

    # then
    assert result == {"test_1": 1, "test_2": 2, "test_3": -3}


def test_parse_qs_with_array_values() -> None:
    # when
    result = parse_qs("test_1[]=1&test_1[]=2&test_1[]=3")

    # then
    assert result == {"test_1": [1, 2, 3]}


def test_parse_qs_with_dict_values() -> None:
    # when
    result = parse_qs("test_1[a]=1&test_1[b]=2&test_1[c]=3")

    # then
    assert result == {"test_1": {"a": 1, "b": 2, "c": 3}}


def test_parse_qs_with_nested_arrays() -> None:
    # when
    result = parse_qs("test_1[][]=1&test_1[][]=2&test_1[][]=3")

    # then
    assert result == {"test_1": [[1], [2], [3]]}


def test_parse_qs_with_indexed_arrays() -> None:
    # when
    result = parse_qs("test_1[0][]=1&test_1[0][]=2&test_1[0][]=3")

    # then
    assert result == {"test_1": {"0": [1, 2, 3]}}


def test_parse_qs_with_broken_key() -> None:
    # when
    result = parse_qs("test_1[[a][b]]=1&test_1[b]=2&test_1[c]=3")

    # then
    assert result == {"test_1[[a][b]]": 1, "test_1": {"b": 2, "c": 3}}


def test_query_string_instantiation() -> None:
    # when
    instance = HttpQueryString("test_1[0][]=1&test_1[0][]=2&test_1[0][]=3")

    # then
    assert "test_1" in instance
    assert instance["test_1"] == {"0": [1, 2, 3]}


def test_query_string_with_repeated_key() -> None:
    # when
    result = parse_qs("test_1=1&test_1=2&test_1=3")

    # then
    assert result == {"test_1": [1, 2, 3]}


def test_query_string_with_repeated_key_and_arrays() -> None:
    # when
    result = parse_qs("test_1=1&test_1[]=2&test_1[]='3'")

    # then
    assert result == {"test_1": [1, 2, "'3'"]}


def test_query_string_with_repeated_key_and_dict() -> None:
    # when
    result = parse_qs("test_1=1&test_1[a]=2&test_1[b]=3")

    # then
    assert result == {"test_1": {"": 1, "a": 2, "b": 3}}


@mark.parametrize(
    "query_string,expected",
    [
        ["a=1", {"a": 1}],
        ["a%5B%5D=1", {"a": [1]}],
        ["a%5Ba%5D=1", {"a": {"a": 1}}],
    ],
)
def test_quoted_query_string(query_string: str, expected: dict) -> None:
    assert parse_qs(query_string) == expected


def test_compare_query_string() -> None:
    # given
    qs = HttpQueryString("")
    qs_copy = HttpQueryString("")

    # then
    assert qs == qs_copy

    # when
    qs = HttpQueryString("param=1")

    # then
    assert not qs == qs_copy

    # when
    qs_copy = HttpQueryString("param=1")

    # then
    assert qs == qs_copy


def test_can_parse_floats_in_query() -> None:
    # when
    result = parse_qs("a=12.4312&b=-13.12")

    # then
    assert result == {"a": 12.4312, "b": -13.12}


def test_can_parse_booleans_in_query() -> None:
    # when
    result = parse_qs("a=true&b=false")

    # then
    assert result == {"a": True, "b": False}


def test_ignores_string_integers_starting_with_0() -> None:
    # when
    result = parse_qs("not_integer=01231&float=0.123&not_float=01.23&zero=0")

    # then
    assert result == {
        "not_integer": "01231",
        "float": 0.123,
        "not_float": "01.23",
        "zero": 0,
    }


def test_can_copy() -> None:
    # given
    qs = HttpQueryString("a=1&b=2&c[a]=1&c[b]=2")

    # when
    qs_copy = deepcopy(qs)
    qs_copy["c"]["a"] = 10

    # then
    assert qs["c"]["a"] == 1
