# 환경 설정

`environment.env.example`을 `environment.env`로 복사하고 모든 항목을 배포 환경에 맞게 입력한다.
`environment.env`는 Git 추적 대상에서 제외한다. 기본값이나 대체값은 제공하지 않는다.

| 항목 | 용도 |
| --- | --- |
| GITEA_DOMAIN | Gitea HTTP 도메인 |
| GITEA_ROOT_URL | 스킴과 마지막 `/`를 포함한 Gitea URL. Runner에도 동일하게 적용한다. |
| GITEA_SSH_DOMAIN | SSH 접속 도메인 |
| GITEA_HTTP_NODE_PORT | HTTP NodePort 번호 |
| GITEA_SSH_PORT | SSH NodePort 및 Gitea가 안내하는 SSH 포트 번호 |
| STORAGE_CLASS | Gitea, PostgreSQL, Runner의 스토리지 클래스 |
| RUNNER_TIMEZONE | Runner 시간대 |
| GITEA_ADMIN_EMAIL | 관리자 이메일 |
| GITEA_DATABASE_HOST | PostgreSQL 접속 주소와 포트 |

저장소 루트에서 다음 명령으로 렌더링한다.

```sh
kubectl kustomize applications
```

환경 파일이 없으면 렌더링이 실패한다. 예제의 빈 값은 배포값이 아니므로 모두 입력해야 한다.
개별 Application YAML에는 외부 설정 주입 대상인 빈 문자열과 숫자 `0`이 있으므로 직접 적용하지 않는다.
Kustomize가 환경값을 주입한 결과를 배포에 사용한다. 설정 전달용 ConfigMap은 출력에서 제외한다.
Argo CD가 이 디렉터리를 렌더링하는 경우에도 해당 렌더링 환경에 `environment.env`를 공급해야 한다.

노드 선택 조건은 제거했다. 차트 버전, 애플리케이션 이름, Secret 참조, 컨테이너 권한 및 기능 설정은 유지한다.
