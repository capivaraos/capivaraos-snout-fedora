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
ISO_NAME=CapivaraOS-Snout-1.0.0-x86_64.iso
PKG_VERSION=1.0.0

echo "==> 1/4: Instalando dependências (lorax, rpm-build, ImageMagick, git, createrepo_c)..."
sudo dnf install -y lorax rpm-build ImageMagick git createrepo_c

echo "==> 2/4: Construindo RPM capivaraos-branding..."
"$SCRIPT_DIR/rpm/build-rpm.sh"

echo "==> 3/4: Criando repositório local em ${REPO_DIR}..."
# NOTA: ~/rpmbuild/RPMS/noarch/ pode acumular RPMs capivaraos-branding de
# OUTRAS spins (Marsh/Pup, com Requires diferentes -- sddm/lightdm-gtk em
# vez de gdm) caso já tenham sido buildadas na mesma máquina. Copiar com
# glob "capivaraos-branding-*.rpm" pegaria todas e o dnf veria múltiplos
# pacotes conflitantes com o mesmo nome — por isso o repositório local é
# limpo e recebe APENAS a versão desta spin (${PKG_VERSION}).
rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"
cp -v "$HOME/rpmbuild/RPMS/noarch/capivaraos-branding-${PKG_VERSION}-"*.rpm "$REPO_DIR/"
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
    --volid="CapivaraOS Snout 1.0.0" --variant="CapivaraOS Snout" \
    --releasever=44

echo
echo "==> Concluído! ISO em: ${RESULT_DIR}/${ISO_NAME}"
