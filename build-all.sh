#!/bin/bash
# Build completo do CapivaraOS Snout (Fedora 44 GNOME): instala
# dependências, gera o RPM capivaraos-branding, monta um repositório local
# com ele e constrói a ISO live com livemedia-creator.
#
# Requer privilégios de root (dnf install + livemedia-creator --no-virt) e
# acesso à rede (pacotes do Fedora). Recomenda-se rodar num terminal
# interativo (a senha do sudo será solicitada e o build pode levar bastante
# tempo).
#
# Uso:
#   ./build-all.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR=/var/tmp/capivaraos-snout-repo
RESULT_DIR=/var/tmp/capivaraos-snout-result
ISO_NAME=CapivaraOS-Snout-1.0.7-x86_64.iso

echo "==> 1/4: Instalando dependências (lorax, rpm-build, ImageMagick, git, createrepo_c)..."
sudo dnf install -y lorax rpm-build ImageMagick git createrepo_c

echo "==> 2/4: Construindo RPM capivaraos-branding..."
"$SCRIPT_DIR/rpm/build-rpm.sh"

echo "==> 3/4: Criando repositório local em ${REPO_DIR}..."
# BUG CORRIGIDO (build anterior): ~/rpmbuild/RPMS/noarch/ acumula RPMs
# "capivaraos-branding" de TODAS as spins buildadas na mesma máquina (Marsh,
# Pup, Snout). Um filtro por versão sozinho não basta -- num build real,
# Pup e Snout compartilhavam a mesma Version (1.0.0) e o dnf instalou
# silenciosamente o RPM do Pup no lugar do Snout (Release mais alto
# "ganhava"), causando wallpapers/seletor de fundo errados e
# Requires=lightdm-gtk incompatível.
# Agora resolvemos a NEVRA EXATA deste spec (Version E Release) via
# "rpmspec -q", garantindo que copiamos só o RPM desta spin, independente
# do que mais estiver no diretório compartilhado.
NEVRA=$(rpmspec -q --qf '%{name}-%{version}-%{release}.%{arch}\n' "$SCRIPT_DIR/rpm/capivaraos-branding.spec" | head -1)
RPM_FILE="$HOME/rpmbuild/RPMS/noarch/${NEVRA}.rpm"
[ -f "$RPM_FILE" ] || { echo "ERRO: RPM esperado não encontrado: ${RPM_FILE}" >&2; exit 1; }
sudo rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"
cp -v "$RPM_FILE" "$REPO_DIR/"
createrepo_c "$REPO_DIR"

echo "==> 4/4: Gerando ISO com livemedia-creator (pode levar bastante tempo)..."
sudo rm -rf "$RESULT_DIR"

# O anaconda (rodando via --no-virt/unshare) resolve "%include caminho.ks"
# em relação ao seu próprio cwd, que não é o diretório deste projeto — por
# isso "achatamos" o kickstart num único arquivo sem %include antes de
# chamar o livemedia-creator. Ver kickstart/ks-flatten.py.
FLAT_KS=/var/tmp/capivaraos-snout-flat.ks
( cd "$SCRIPT_DIR/kickstart" && python3 ks-flatten.py capivaraos-snout.ks > "$FLAT_KS" )

sudo livemedia-creator --ks="$FLAT_KS" \
    --no-virt --resultdir="$RESULT_DIR" \
    --project="CapivaraOS Snout" --make-iso --iso-only \
    --iso-name="$ISO_NAME" \
    --volid="CapivaraOS Snout 1.0.7" --variant="CapivaraOS Snout" \
    --releasever=44

echo
echo "==> Concluído! ISO em: ${RESULT_DIR}/${ISO_NAME}"
