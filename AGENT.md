# 애플리케이션 배포 규칙

- 작업을 시작할 때마다 이 파일의 지침을 확인한다.
- Application 추가 완료 후 클러스터에 배포하고 Git push까지 수행한다.
- 애플리케이션을 추가할 때는 기존 애플리케이션과 동일하게 Argo CD Application의 Helm 구성으로 배포한다.
- KFP standalone은 사용자 요청에 따라 공식 Kustomize 구성을 Argo CD Application으로 배포한다.

# 클러스터 접속 규칙

- 사용자는 항상 KubeVPN을 실행 중이므로 Kubernetes Service 주소(`svc`)를 기준으로 작업한다.
- 클러스터 서비스 접속 시 포트 포워딩이나 localhost 주소로 변경하지 않는다.
