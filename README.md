# sorter simulator algorithm poc

simulation_window 에 셀 정보 띄울 label을 만들어 두었습니다

아직은 빈 셀에 graphicsitem 이 없습니다

아마 클릭 이벤트 넣으려면 graphicsitem 의 mousepressevent 핸들러 구현하시면 될거같습니다

## optimization for later

fix duplicates
currently, generate all path include duplicates


cell

no direction!!!

say to team

my app have error
when robots added on grid
what is status on each cell

로봇 큐에 들어갈때 중간에 들어가게 할 수 있게 할것인지?

        # detect deadlock
        # self.wait : int
        # and count wait ??

멘토님께 현재 알고리즘 설명하고
위에 wait 부분도 설명하고

제가 구현한 알고리즘은 로봇이 한칸 움직일 때마다 자신 앞에 로봇이 있는지를 확인
논문에서는 로봇이 루트를 처음 받을 때 충돌할 것인지를 확인

로봇 경로가 막히면 그 칸을 제외하고 다시 경로를 탐색하는 건 있음
데드락 탐지를 로봇이 몇 턴 기다리는지 카운트하는 건 어떤지?

월요일 목요일에 각자 그동안 한 거 회의하는걸로
한거 없어도 괜찮으니까

데드락이 걸리는 조건이 뭐지?


일방통행 셀
물건 ㄷ랍 후 옆으로 빠져나옴 (일방통행)

대기 위치가 슈트 경로인데 

보틀넥 시 뒤로 몇칸 후진 후 경로재설정

두 로봇이 마주보는 경우 일단 후진

일단 e2e 되도록 다 완성시켜놓기

디버깅용으로 셀에 일방통행이면 화살표 표시하기
일방통행 셀은 나가는 방향이 하나이고 들어오는건 다른방향에서 가능

회의 후
마주볼때 뒤로가는거면 계속 뒤로가는 경우도 있지 않나?