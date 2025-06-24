# Тренування моделей та трекінг експериментів

## Необхідні налаштування
1. Акаунти у AWS, W&B
2. Розгорнутий Ray кластер 

### Розгортання Ray Cluster
Встановлення Ray
```bash
pyenv install 3.10
pyenv shell 3.10
python -m venv .venv
source .venv/bin/activate
pip install boto3
pip install -U "ray[all]"
```
### AWS
Конфігурування кластера відбувається через файл `cluster-config.yaml`, який далі використовується для його запуску:
```bash
ray up -y ray-aws/cluster-config-aws.yaml
```
Зупинка кластера 
```bash
ray down ray-aws/cluster-config-aws.yaml
```
Приклад [ray-aws/cluster-config-aws.yaml](cluster-config-aws.yaml) для розгортання в AWS

Щоб знайти правильний імідж для розгортання
```bash
aws ec2 describe-images --region us-east-2 --owners amazon \ 
--filters 'Name=name,Values=Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04) *' 'Name=state,Values=available' \
--query 'reverse(sort_by(Images, &CreationDate))[:1].ImageId' --output text
```

https://docs.amazonaws.cn/en_us/dlami/latest/devguide/what-is-dlami.html
https://docs.ray.io/en/latest/cluster/vms/references/ray-cluster-configuration.html
https://docs.ray.io/en/latest/cluster/vms/references/ray-cluster-cli.html

## Тренування моделі на Ray кластері

Спочатку перевіряємо роботу тренування локально
```bash
pip install -r requirements.txt
python train.py
```
Тепер перевіряємо, щоб працював запуск тренування на кластері з локального середовища
```bash
python run_ray_training.py
```

Перевіряємо дані експерименту та створюємо нову версію моделі у W&B

## Створення локального Kubernetes кластеру

### Встановлення інструментів командного рядка
```bash
# Встановлення kubectl
brew install kubectl

# Встановлення kind для локального кластера Kubernetes
brew install kind

# Встановлення kustomize для управління YAML конфігураціями
brew install kustomize

# Встановлення helm для управління пакетами Kubernetes
brew install helm
```

### Встановлення Docker Desktop
Встановіть Docker Desktop з виділенням не менше 8GB пам'яті

### Рекомендовані інструменти 
Для зручної взаємодії з кластером можна встановити візуальний інструмент:
https://k8slens.dev/

## Розгортання локального K8s та Ray кластеру

### Підготовка

У директорії `week-3/k8s/` вже підготовлені всі необхідні конфігураційні файли:

- `kind/kind-config.yaml` - конфігурація локального Kubernetes кластера
- `ray-cluster-values.yaml` - параметри Ray кластера для Helm
- `setup_cluster.sh` - автоматичний скрипт розгортання

### Розгортання кластера

```bash
# Перейдіть у директорію з конфігураціями
cd week-3/k8s/

# Зробіть скрипт виконуваним
chmod +x setup_cluster.sh

# Запустіть автоматичне розгортання
./setup_cluster.sh
```

Скрипт виконає наступні дії:
1. Створить Kind кластер
2. Встановить KubeRay operator через Helm
3. Розгорне Ray кластер з налаштованими параметрами
4. Налаштує port-forwarding для доступу до сервісів

### Перевірка роботи кластера

```bash
# Перевірте статус подів
kubectl get pods

# Перевірте статус Ray кластера
kubectl exec $(kubectl get pod -l ray.io/node-type=head -o jsonpath='{.items[0].metadata.name}') -- ray status

# Відкрийте Ray Dashboard у браузері
http://localhost:8265
```

### Доступні сервіси

Після успішного розгортання будуть доступні:

- **Ray Dashboard**: http://localhost:8265 - веб-інтерфейс для моніторингу кластера
- **Ray Client**: `ray://localhost:10001` - endpoint для підключення Python клієнта
- **Ray Serve**: http://localhost:8000 - endpoint для розгортання моделей

### Запуск тестової задачі

```bash
# Через Ray Jobs API
ray job submit --address http://localhost:8265 -- python -c "import ray; ray.init(); print(ray.cluster_resources())"

# Або через Python клієнт
python -c "
import ray
ray.init('ray://localhost:10001')
print('Ray cluster resources:', ray.cluster_resources())
ray.shutdown()
"
```

### Навчання моделі на KubeRay выкористовуючи CPU

```bash
cd yolo-cpu
python submit_job.py
```

### Управління кластером

```bash
# Зупинити port forwarding
pkill -f 'kubectl port-forward.*raycluster-kuberay-head-svc'

# Видалити Ray кластер
helm uninstall raycluster
helm uninstall kuberay-operator

# Повністю видалити Kind кластер
kind delete cluster --name ray-cluster

# Перезапустіть кластер з нуля
kind delete cluster --name ray-cluster
./setup_cluster.sh
```
