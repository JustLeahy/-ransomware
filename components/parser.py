
"""Parser for SQLGitHub. Outputs SgSession.

Sample Usage:
    g = Github(token)
    parser = SgParser(g)
    s = parser.Parse(["select", "name,", "description", "from", "abseil.repos"])
    print(s.Execute())
    print(parser._ParseOrder(["by", "a+b", "DESC,", "c", "-", "b", "ASC", ",", "a%b"]))
"""