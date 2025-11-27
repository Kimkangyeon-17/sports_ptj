const { createApp, ref, computed, onMounted, watch } = Vue;

// API Base URL (Django 서버)
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// 1. Main Dashboard Component
const MainDashboard = {
  template: '#main-dashboard-template',
  setup() {
    // 1. 상태 관리 (현재 선택된 팀 ID)
    const currentTeamId = ref('team1');

    // 2. 목업 데이터
    const teams = {
      team1: {
        name: 'My Team (서울)',
        icon: 'fa-solid fa-shield-cat',
        aiWinRate: '65%',
        nextMatch: {
          date: '2025.11.24 (일) 20:00',
          opponent: 'Dragons',
          opponentIcon: 'fa-solid fa-dragon'
        },
        stats: {
          rank: '3위',
          winRate: '75%',
          record: '15승 4무 3패',
          recent: '승-승-무-패-승'
        },
        news: [
          '주전 공격수 부상, 2주 결장 예상',
          '리그 우승 경쟁, 더욱 치열해져',
          '감독 인터뷰: "다음 경기가 중요"'
        ]
      },
      team2: {
        name: 'My Team 2 (이글스)',
        icon: 'fa-solid fa-feather-pointed',
        aiWinRate: '40%',
        nextMatch: {
          date: '2025.11.25 (월) 19:30',
          opponent: 'Tigers',
          opponentIcon: 'fa-solid fa-cat'
        },
        stats: {
          rank: '1위',
          winRate: '88%',
          record: '18승 2무 2패',
          recent: '승-승-승-승-무'
        },
        news: [
          '이글스, 파죽의 4연승 질주',
          'MVP 후보 1순위, 이글스 에이스 선정',
          '홈 경기장 만석 예상'
        ]
      },
      team3: {
        name: 'My Team 3 (샤크스)',
        icon: 'fa-solid fa-fish-fins',
        aiWinRate: '52%',
        nextMatch: {
          date: '2025.11.26 (화) 20:00',
          opponent: 'Bears',
          opponentIcon: 'fa-solid fa-paw'
        },
        stats: {
          rank: '7위',
          winRate: '45%',
          record: '8승 5무 9패',
          recent: '패-패-승-무-패'
        },
        news: [
          '샤크스, 분위기 반전이 필요하다',
          '새로운 용병 영입 오피셜 떴다',
          '팬 간담회 개최 예정'
        ]
      }
    };

    // 3. 현재 선택된 팀의 데이터를 반환하는 Computed Property
    const currentTeamData = computed(() => {
      return teams[currentTeamId.value];
    });

    // 4. 팀 변경 함수
    const changeTeam = (teamKey) => {
      currentTeamId.value = teamKey;
    };

    return {
      currentTeamId,
      teams,
      currentTeamData,
      changeTeam
    };
  }
};

// 2. Common Page Component (Placeholder)
const CommonPage = {
  template: '#common-page-template',
  props: ['title', 'icon']
};

// 3. Define other components using CommonPage
const SoccerNews = {
  components: { CommonPage },
  template: '<CommonPage title="축구 뉴스" icon="fa-regular fa-newspaper" />'
};

const MatchSchedule = {
  components: { CommonPage },
  template: '<CommonPage title="경기 일정" icon="fa-regular fa-calendar" />'
};

// API 응답 파싱 헬퍼 (배열 또는 페이지네이션 객체 처리)
const parseApiResponse = (data) => {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.results)) return data.results;
  return [];
};

// 순위표 컴포넌트
const Standings = {
  template: '#standings-template',
  setup() {
    const standings = ref([]);
    const loading = ref(true);
    const error = ref(null);

    const fetchStandings = async () => {
      loading.value = true;
      error.value = null;
      try {
        const response = await fetch(`${API_BASE_URL}/standings/`);
        if (!response.ok) throw new Error('데이터를 불러오는데 실패했습니다.');
        const data = await response.json();
        standings.value = parseApiResponse(data);
      } catch (e) {
        error.value = e.message;
      } finally {
        loading.value = false;
      }
    };

    onMounted(fetchStandings);

    return { standings, loading, error };
  }
};

// 팀 검색 컴포넌트
const TeamSearch = {
  template: '#team-search-template',
  setup() {
    const teams = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const searchQuery = ref('');
    const currentPage = ref(1);
    const itemsPerPage = 10;

    const fetchTeams = async () => {
      loading.value = true;
      error.value = null;
      try {
        const response = await fetch(`${API_BASE_URL}/teams/`);
        if (!response.ok) throw new Error('데이터를 불러오는데 실패했습니다.');
        const data = await response.json();
        teams.value = parseApiResponse(data);
      } catch (e) {
        error.value = e.message;
      } finally {
        loading.value = false;
      }
    };

    const filteredTeams = computed(() => {
      if (!searchQuery.value) return teams.value;
      return teams.value.filter(team =>
        team.team_name.toLowerCase().includes(searchQuery.value.toLowerCase())
      );
    });

    const totalPages = computed(() => Math.ceil(filteredTeams.value.length / itemsPerPage));

    const paginatedTeams = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage;
      return filteredTeams.value.slice(start, start + itemsPerPage);
    });

    watch(searchQuery, () => { currentPage.value = 1; });

    onMounted(fetchTeams);

    return { teams, loading, error, searchQuery, currentPage, totalPages, paginatedTeams, itemsPerPage, filteredTeams };
  }
};

// 코치 검색 컴포넌트
const CoachSearch = {
  template: '#coach-search-template',
  setup() {
    const staff = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const searchQuery = ref('');
    const teamFilter = ref('');
    const positionFilter = ref('');
    const currentPage = ref(1);
    const itemsPerPage = 10;

    const fetchStaff = async () => {
      loading.value = true;
      error.value = null;
      try {
        const response = await fetch(`${API_BASE_URL}/staff/`);
        if (!response.ok) throw new Error('데이터를 불러오는데 실패했습니다.');
        const data = await response.json();
        staff.value = parseApiResponse(data);
      } catch (e) {
        error.value = e.message;
      } finally {
        loading.value = false;
      }
    };

    const teamList = computed(() => [...new Set(staff.value.map(s => s.team_name))].sort());
    const positionList = computed(() => [...new Set(staff.value.map(s => s.position))].sort());

    const filteredStaff = computed(() => {
      return staff.value.filter(s => {
        const matchesSearch = !searchQuery.value || 
          s.name.toLowerCase().includes(searchQuery.value.toLowerCase());
        const matchesTeam = !teamFilter.value || s.team_name === teamFilter.value;
        const matchesPosition = !positionFilter.value || s.position === positionFilter.value;
        return matchesSearch && matchesTeam && matchesPosition;
      });
    });

    const totalPages = computed(() => Math.ceil(filteredStaff.value.length / itemsPerPage));

    const paginatedStaff = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage;
      return filteredStaff.value.slice(start, start + itemsPerPage);
    });

    watch([searchQuery, teamFilter, positionFilter], () => { currentPage.value = 1; });

    onMounted(fetchStaff);

    return { staff, loading, error, searchQuery, teamFilter, positionFilter, currentPage, totalPages, paginatedStaff, itemsPerPage, filteredStaff, teamList, positionList };
  }
};

// 선수 검색 컴포넌트
const PlayerSearch = {
  template: '#player-search-template',
  setup() {
    const players = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const searchQuery = ref('');
    const teamFilter = ref('');
    const positionFilter = ref('');
    const currentPage = ref(1);
    const itemsPerPage = 10;

    const fetchPlayers = async () => {
      loading.value = true;
      error.value = null;
      try {
        const response = await fetch(`${API_BASE_URL}/players/`);
        if (!response.ok) throw new Error('데이터를 불러오는데 실패했습니다.');
        const data = await response.json();
        players.value = parseApiResponse(data);
      } catch (e) {
        error.value = e.message;
      } finally {
        loading.value = false;
      }
    };

    const teamList = computed(() => [...new Set(players.value.map(p => p.team_name).filter(Boolean))].sort());
    const positionList = computed(() => [...new Set(players.value.map(p => p.position).filter(Boolean))].sort());

    const filteredPlayers = computed(() => {
      return players.value.filter(p => {
        const matchesSearch = !searchQuery.value || 
          p.name.toLowerCase().includes(searchQuery.value.toLowerCase());
        const matchesTeam = !teamFilter.value || p.team_name === teamFilter.value;
        const matchesPosition = !positionFilter.value || p.position === positionFilter.value;
        return matchesSearch && matchesTeam && matchesPosition;
      });
    });

    const totalPages = computed(() => Math.ceil(filteredPlayers.value.length / itemsPerPage));

    const paginatedPlayers = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage;
      return filteredPlayers.value.slice(start, start + itemsPerPage);
    });

    watch([searchQuery, teamFilter, positionFilter], () => { currentPage.value = 1; });

    onMounted(fetchPlayers);

    return { players, loading, error, searchQuery, teamFilter, positionFilter, currentPage, totalPages, paginatedPlayers, itemsPerPage, filteredPlayers, teamList, positionList };
  }
};


// 4. Create App
const app = createApp({
  components: {
    MainDashboard,
    SoccerNews,
    MatchSchedule,
    Standings,
    TeamSearch,
    CoachSearch,
    PlayerSearch
  },
  setup() {
    const currentView = ref('MainDashboard');
    const isAiModalOpen = ref(false);

    const toggleAiModal = () => {
      isAiModalOpen.value = !isAiModalOpen.value;
    };

    const currentViewTitle = computed(() => {
      const titles = {
        'MainDashboard': '메인 대시보드',
        'SoccerNews': '축구 뉴스',
        'MatchSchedule': '경기 일정',
        'Standings': '순위표',
        'TeamSearch': '팀 검색',
        'CoachSearch': '감독/코치 검색',
        'PlayerSearch': '선수 검색'
      };
      return titles[currentView.value] || 'Soccer Data';
    });

    return {
      currentView,
      currentViewTitle,
      isAiModalOpen,
      toggleAiModal
    };
  }
});

app.mount('#app');
