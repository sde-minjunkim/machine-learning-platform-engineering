# Machine Learning Platform Engineering

기존 Argo CD에서 상위 Application 하나를 적용하면 이 저장소를 기준으로 CNPG, PostgreSQL, Gitea, Gitea Runner를 설치한다. Argo CD 자체는 설치 대상에 포함하지 않는다.

## 구조

```text
bootstrap/
  application-health.yaml   # 상위 Application이 하위 Application 준비 상태를 확인하는 설정
  root-application.yaml     # Git의 applications/를 관리하는 상위 Application
applications/
  prerequisites.yaml        # Git의 resources/를 관리한다
  cnpg.yaml                 # CNPG Operator Helm 차트
  gitea-db.yaml             # PostgreSQL Cluster Helm 차트
  gitea.yaml                # Gitea Helm 차트
  gitea-runner.yaml         # Runner Helm 차트
resources/
  kustomization.yaml        # 보조 리소스 목록
  namespaces.yaml           # cnpg-system, gitea 네임스페이스
  gitea-*-pv.yaml            # 정적 영구 볼륨
  gitea-pvc.yaml             # Gitea 볼륨 요청
  gitea-db-volume-permissions.yaml # PostgreSQL 경로 권한 설정 Job
```

## 설치

Kubernetes와 Argo CD가 이미 준비돼 있어야 한다. 현재 구성은 노드 `debian`, IP `192.168.1.254`, control-plane taint가 있는 단일 노드를 기준으로 한다.

```sh
git clone https://github.com/sde-minjunkim/machine-learning-platform-engineering.git
cd machine-learning-platform-engineering
# 신규 클러스터에서는 아래의 Secret 사전 생성 단계를 먼저 수행한다.
kubectl apply --server-side --field-manager=platform-bootstrap -f bootstrap/
```

상위 Application `machine-learning-platform`은 이 Git 저장소의 `main` 브랜치를 추적한다. 필수 리소스 Application도 같은 브랜치의 `resources/`를 추적한다. 나머지 Application은 공식 Helm 저장소의 차트 버전을 고정해서 사용한다.

초기 적용에는 관리자의 클러스터 권한이 필요하다. `application-health.yaml`은 기존 `argocd-cm`에 하위 Application 상태 판정 키만 추가한다. Argo CD를 재설치하거나 기존 설정 전체를 대체하지 않는다.

## 설치 순서

| Sync wave | Application | 완료 조건 |
| --- | --- | --- |
| -40 | prerequisites | 네임스페이스, PV/PVC 적용 및 권한 설정 Job 완료 |
| -30 | cnpg | CNPG Operator 준비 완료 |
| -20 | gitea-db | PostgreSQL Cluster 준비 완료 |
| -10 | gitea | Gitea 준비 완료 |
| 0 | gitea-runner | Runner 준비 완료 |

상위 Application은 하위 Application이 `Synced`이면서 `Healthy`가 될 때까지 다음 wave를 진행하지 않는다. PostgreSQL Cluster 상태는 Argo CD 3.5.6에 포함된 CNPG health 판정을 사용한다.

## 계정과 저장소

Gitea와 PostgreSQL 계정명은 `admin`이다. 비밀번호와 Runner 등록 토큰은 Git에 포함하지 않고 클러스터의 Secret에서 읽는다. Gitea는 PostgreSQL에 TLS로 연결한다.

기존 클러스터에는 필요한 Secret이 이미 생성돼 있다. 신규 클러스터에서는 상위 Application을 적용하기 전에 다음 단계로 Secret을 생성해야 한다. 이 단계를 생략하면 PostgreSQL과 Gitea가 준비되지 않으며 이후 설치가 진행되지 않는다.

```sh
kubectl apply -f resources/namespaces.yaml
read -r -s -p 'Gitea/PostgreSQL 비밀번호: ' PLATFORM_PASSWORD
export PLATFORM_PASSWORD
export RUNNER_REGISTRATION_TOKEN="$(openssl rand -hex 24)"

kubectl -n gitea create secret generic gitea-admin \
  --from-literal=username=admin \
  --from-literal=password="${PLATFORM_PASSWORD:?}" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl -n gitea create secret generic gitea-db-credentials \
  --type=kubernetes.io/basic-auth \
  --from-literal=username=admin \
  --from-literal=password="${PLATFORM_PASSWORD:?}" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl -n gitea create secret generic gitea-runner-token \
  --from-literal=token="${RUNNER_REGISTRATION_TOKEN:?}" \
  --dry-run=client -o yaml | kubectl apply -f -
```

Runner 등록 토큰은 최소 32자여야 한다. 이미 설치된 클러스터에서는 기존 Secret을 유지한다. 위 명령은 신규 설치의 사전 준비 단계이며, Secret 값의 생성·변경은 Git 동기화 대상에서 제외한다.

| 대상 | 주소 또는 경로 |
| --- | --- |
| Gitea HTTP | http://192.168.1.254:30080 |
| Gitea SSH | 192.168.1.254:30222 |
| PostgreSQL | gitea-db-rw.gitea.svc.cluster.local:5432, DB gitea |
| Gitea PV | /var/lib/gitea, 10Gi |
| PostgreSQL PV | /var/lib/cnpg/gitea-db, 10Gi |
| Runner PV | /var/lib/gitea-runner, 1Gi |

노드 경로는 hostPath를 사용하고 PV에는 Retain 정책을 적용한다. PostgreSQL은 단일 인스턴스다. 다른 클러스터에 설치할 때에는 Git에서 노드명, IP, 저장소 경로와 용량을 수정해야 한다.

## 변경 반영과 상태 확인

Git의 `main`에 변경 사항이 반영되면 Argo CD가 자동 동기화한다. 선언한 리소스의 수동 변경은 self-heal로 복원한다. 자동 prune은 비활성화하므로 Git에서 파일을 제거하더라도 클러스터의 리소스를 자동으로 삭제하지 않는다.

```sh
kubectl -n argocd get applications
kubectl -n gitea get pods,cluster,pvc
kubectl -n cnpg-system get pods
```

Helm 기반 Application은 Argo CD가 차트를 렌더링하고 리소스를 관리한다. 별도의 Helm 릴리스로 등록되지 않으므로 `helm list`에는 나타나지 않는다.
