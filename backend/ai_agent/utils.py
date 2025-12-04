# ai_agent/utils.py

"""
유틸리티 함수들
"""

# 한글-영문 팀명 매핑
TEAM_NAME_MAPPING = {
    # 한글 -> 영문
    "아스날": "Arsenal",
    "리버풀": "Liverpool",
    "맨시티": "Manchester City",
    "맨유": "Manchester United",
    "맨체스터 유나이티드": "Manchester United",
    "맨체스터 시티": "Manchester City",
    "첼시": "Chelsea",
    "토트넘": "Tottenham Hotspur",
    "뉴캐슬": "Newcastle United",
    "브라이튼": "Brighton & Hove Albion",
    "웨스트햄": "West Ham United",
    "애스턴 빌라": "Aston Villa",
    "풀럼": "Fulham",
    "크리스탈 팰리스": "Crystal Palace",
    "울버햄튼": "Wolverhampton Wanderers",
    "울버햄프턴": "Wolverhampton Wanderers",
    "노팅엄": "Nottingham Forest",
    "브렌트포드": "Brentford",
    "에버턴": "Everton",
    "본머스": "Bournemouth",
    "루턴": "Luton Town",
    "번리": "Burnley",
    "셰필드": "Sheffield United",
    "레스터": "Leicester City",
    "사우샘프턴": "Southampton",
    "리즈": "Leeds United",
}

# 영문 약어 -> 정식 명칭
TEAM_ABBR_MAPPING = {
    "ARS": "Arsenal",
    "LIV": "Liverpool",
    "MCI": "Manchester City",
    "MUN": "Manchester United",
    "CHE": "Chelsea",
    "TOT": "Tottenham Hotspur",
    "NEW": "Newcastle United",
}


def normalize_team_name(team_name: str | None) -> str | None:
    """
    팀 이름을 정규화 (한글 -> 영문, 약어 -> 정식)

    Args:
        team_name: 원본 팀 이름

    Returns:
        정규화된 팀 이름 (영문 정식 명칭)
    """
    if not team_name:
        return None

    # 1. 한글 매핑 체크
    if team_name in TEAM_NAME_MAPPING:
        return TEAM_NAME_MAPPING[team_name]

    # 2. 약어 매핑 체크
    if team_name.upper() in TEAM_ABBR_MAPPING:
        return TEAM_ABBR_MAPPING[team_name.upper()]

    # 3. 부분 매칭 (contains)
    team_name_lower = team_name.lower()
    for kr, en in TEAM_NAME_MAPPING.items():
        if kr in team_name or team_name in kr:
            return en

    # 4. 원본 그대로 반환
    return team_name


def normalize_player_name(player_name: str | None) -> str | None:
    """
    선수 이름 정규화 (필요시 확장)

    Args:
        player_name: 원본 선수 이름

    Returns:
        정규화된 선수 이름
    """
    if not player_name:
        return None

    # 한글 선수명 매핑 (필요시 추가)
    player_mapping = {
        "손흥민": "Son Heung-Min",
        "황희찬": "Hwang Hee-Chan",
        "김민재": "Kim Min-Jae",
    }

    return player_mapping.get(player_name, player_name)
