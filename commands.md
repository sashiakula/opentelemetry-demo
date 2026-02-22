# ================================
# 🧰 System update & base tools
# ================================
sudo apt-get update
sudo apt install -y make
sudo apt-get install -y dos2unix yamllint
sudo apt-get install -y curl ca-certificates

# (optional alternative installs via snap)
# sudo snap install kubectl --classic
# sudo snap install helm

# ================================
# 👤 Docker permission setup
# ================================
sudo usermod -aG docker $USER
newgrp docker   # or logout/login

# Verify docker works
docker version

# ================================
# 🚢 Install KIND (Kubernetes in Docker)
# ================================
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.23.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Verify kind
kind --version

# ================================
# 🏗️ Create / check KIND cluster
# ================================
kind create cluster --name mykind --config kind-config.yaml
kind get clusters

# ================================
# ☸️ Install kubectl (if not present)
# ================================
# (use ONE method)

# Method A — apt (if available in your repo)
sudo apt-get install -y kubectl

# Method B — snap (more reliable on Ubuntu)
# sudo snap install kubectl --classic

# Verify cluster
kubectl get nodes

# ================================
# 🚀 Install Helm (recommended script)
# ================================
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version

# ================================
# 🧹 YAML cleanup
# ================================
dos2unix opentelemetry-demo.yaml
dos2unix opentelemetry-demo-monitoring.yml
sed -i 's/[ \t]*$//' opentelemetry-demo-monitoring.yml

# ================================
# 🔍 YAML linting
# ================================
yamllint -d relaxed opentelemetry-demo.yaml
yamllint -d relaxed opentelemetry-demo-monitoring.yml

# ================================
# 🏭 Generate manifests (project specific)
# ================================
make generate-kubernetes-manifests

# ================================
# 🧪 Validate manifests against cluster
# ================================
kubectl apply --dry-run=client -f opentelemetry-demo-monitoring.yml