# capivaraos-branding — identidade visual do CapivaraOS Snout (Fedora, GNOME)
#
# Equivalente, para a spin GNOME, ao rpm/capivaraos-branding.spec da spin KDE
# (../capivaraos-marsh-fedora/rpm/capivaraos-branding.spec): wallpapers,
# ícones "Sobre o Sistema", tema Plymouth de boot, tela de login GDM,
# /etc/os-release, /etc/issue, avatar padrão.
#
# Diferenças principais em relação à versão KDE (GNOME padrão, sem tema de
# terceiros tipo WhiteSur, sem dock/layout estilo macOS — decisão explícita
# para o Snout):
#   - Sem pacotes de wallpaper "estilo Plasma" (metadata.json); o equivalente
#     GNOME é um único XML em /usr/share/gnome-background-properties/, que
#     registra todos os wallpapers no seletor de fundo do GNOME Settings.
#   - Tela de login: GDM, não SDDM. GDM não tem um "theme.conf.user" como o
#     SDDM/breeze — o wallpaper do greeter é controlado via perfil dconf
#     próprio do GDM (/etc/dconf/profile/gdm + /etc/dconf/db/gdm.d/), que é o
#     mecanismo padrão usado por distros para customizar o fundo do GDM.
#   - Wallpaper do usuário: em vez de um script de runtime (como o
#     capivaraos-set-wallpaper da spin KDE/Xfce), usamos um default dconf
#     system-wide (/etc/dconf/db/local.d/) — aplica-se a qualquer usuário
#     novo sem depender de autostart/timing, e o usuário pode trocar
#     livremente depois (não bloqueamos a chave).
#   - Sem layout de painéis estilo macOS: GNOME Shell padrão (decisão
#     explícita do CapivaraOS Snout, diferente da spin Marsh).

Name:           capivaraos-branding
Version:        1.0.7
Release:        1%{?dist}
Summary:        Identidade visual, wallpapers e branding padrão do CapivaraOS Snout 1.0.7

License:        CC-BY-SA-4.0 AND MIT
URL:            https://capivaraos.org
BuildArch:      noarch

Source0:        %{name}-%{version}.tar.gz

BuildRequires:  ImageMagick
# /usr/bin/convert ou /usr/bin/magick
Requires:       plymouth
Requires:       gdm
Requires:       dconf

# NOTA CapivaraOS: NÃO declaramos "Conflicts: fedora-logos" aqui. Diferente
# da spin KDE (onde sddm/plasma não dependem de fedora-logos), neste Fedora
# 44 o pacote gdm tem uma dependência real em fedora-logos (confirmado via
# "dnf repoquery --whatrequires fedora-logos" no ambiente de build) —
# conflitar com ele tornaria o próprio gdm não instalável. Convivemos com
# fedora-logos instalado (não usamos os arquivos dele em lugar nenhum) e
# sobrescrevemos o que importa (wallpaper, os-release, tema Plymouth) via
# dconf/posttrans, sem remover o pacote.

%description
Pacote de identidade visual do CapivaraOS Snout: wallpapers (incluindo as
fotos de capivaras do Wikimedia Commons, CC BY-SA), conjunto de ícones
"capivaraos-logo" e "capivaraos-full-logo", tema Plymouth de boot, tela de
login GDM, /etc/os-release, /etc/issue e wallpaper padrão do GNOME (via
dconf), com o GNOME Shell padrão (sem customizações de layout).

%prep
%setup -q

%build
set -e
CONVERT=convert
command -v convert >/dev/null 2>&1 || CONVERT=magick

# ── 1. Ícones hicolor "capivaraos-logo" (apenas a capivara, sem texto) ──────
# NOTA: tamanho 36 incluído além do conjunto padrão das outras spins -- é um
# dos tamanhos em que o pacote fedora-logos instala "fedora-logo-icon" (ver
# %post), então precisamos da nossa logo nesse mesmo tamanho para sobrescrevê-lo.
mkdir -p build/icons
for SIZE in 16 22 24 32 36 48 64 96 128 256 512; do
    mkdir -p "build/icons/hicolor/${SIZE}x${SIZE}/apps"
    "$CONVERT" icons/capivaraos-logo.png -resize "${SIZE}x${SIZE}" \
        "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-logo.png"
done

# ── 2. Ícones hicolor "capivaraos-full-logo" (capivara + texto "CapivaraOS") ─
# Usado pelo GNOME Settings ("Sobre") via LOGO= em /etc/os-release, e como
# base para sobrescrever "fedora-logo-icon" (ver %post).
for SIZE in 16 22 24 32 36 48 64 96 128 256 512; do
    mkdir -p "build/icons/hicolor/${SIZE}x${SIZE}/apps"
    "$CONVERT" backgrounds/CapivaraOS_Logo.png -background none -gravity center \
        -extent 1536x1536 -resize "${SIZE}x${SIZE}" \
        "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-full-logo.png"
done

# ── 3. Ícone branco para a área de trabalho ("Instalar CapivaraOS" etc) ─────
mkdir -p build/pixmaps
"$CONVERT" icons/capivaraos-logo.png -fill white -colorize 100% \
    -resize 256x256 build/pixmaps/capivaraos-white.png

# ── 4. Avatar padrão (.face): recorta só a capivara, fundo branco quadrado ──
"$CONVERT" backgrounds/CapivaraOS_Logo.png -crop 1536x600+0+0 +repage -trim +repage \
    -gravity center -background white -extent 1700x1700 \
    -resize 256x256 build/pixmaps/capivaraos-face.png

# ── 4b. Logo quadrada (capivara, sem texto, fundo transparente) para o
# branding do Cockpit/Anaconda WebUI (instalador gráfico da ISO live) ───────
# Ver justificativa detalhada no spec da spin KDE/Pup (mesmo recorte da
# cabeça da capivara, idêntico nas três spins).
mkdir -p build/cockpit
"$CONVERT" backgrounds/CapivaraOS_Logo.png -crop 360x300+480+90 +repage -trim +repage \
    -gravity center -background none -extent 390x390 \
    -resize 256x256 build/cockpit/logo.png
"$CONVERT" build/cockpit/logo.png -resize 32x32 build/cockpit/favicon.ico

# ── 5b. Logo 192x192 para substituir os pixmaps hardcoded do gnome-control-center
# O painel "Sistema" (Sobre) do gnome-control-center no Fedora 44 carrega o
# logo a partir de caminhos FIXOS no código (cc-info-entry.c), independente
# do campo LOGO= no os-release: /usr/share/pixmaps/fedora_logo_med.png (cor)
# e fedora_whitelogo_med.png (branco). Os originais Fedora eram 279x80 px;
# geramos em 192x192 (tamanho máximo do AdwClamp no painel Sobre) para que
# a logo apareça em tela cheia no painel, mais que dobrando o tamanho visual.
# O flag ^ no resize preenche o quadrado (sem barras transparentes) e o
# -extent recorta as bordas para o tamanho exato.
mkdir -p build/pixmaps-med
"$CONVERT" backgrounds/CapivaraOS_Logo.png -background none \
    -resize 192x192^ -gravity center -extent 192x192 \
    build/pixmaps-med/capivaraos-logo-med.png
"$CONVERT" build/pixmaps-med/capivaraos-logo-med.png \
    -fill white -colorize 100% \
    build/pixmaps-med/capivaraos-whitelogo-med.png

# ── 5. Logo BRANCA para o splash do Plymouth (boot/desligamento) ────────────
mkdir -p build/plymouth
"$CONVERT" backgrounds/CapivaraOS_Logo.png -fill white -colorize 100% \
    -resize 320x320 build/plymouth/logo.png

# Spinner branco (arco girando) exibido logo abaixo da logo no splash.
mkdir -p build/plymouth/spinner
"$CONVERT" -size 64x64 xc:none -stroke white -strokewidth 5 \
    -fill none -draw "stroke-linecap round arc 12,12 52,52 0,300" \
    build/plymouth/spinner-base.png
for i in $(seq 0 29); do
    ANG=$(( i * 12 ))
    "$CONVERT" build/plymouth/spinner-base.png -background none \
        -distort SRT ${ANG} +repage "build/plymouth/spinner/${i}.png"
done

%install
set -e
DEFAULT_WP=%{_datadir}/backgrounds/capivaraos/capivaraos-desktop.png

# ── Wallpapers ───────────────────────────────────────────────────────────────
install -d %{buildroot}%{_datadir}/backgrounds/capivaraos
# Todos os wallpapers (incluindo fotos já em 4:3 nativas 1920×1440): direto da fonte
for WP in backgrounds/*.png; do
    install -m 0644 "$WP" %{buildroot}%{_datadir}/backgrounds/capivaraos/
done
install -m 0644 backgrounds/CREDITOS.txt %{buildroot}%{_datadir}/backgrounds/capivaraos/

# ── Pixmaps ──────────────────────────────────────────────────────────────────
install -d %{buildroot}%{_datadir}/pixmaps
install -m 0644 icons/capivaraos.png %{buildroot}%{_datadir}/pixmaps/capivaraos.png
install -m 0644 icons/capivaraos-logo.png %{buildroot}%{_datadir}/pixmaps/capivaraos-logo.png
install -m 0644 build/pixmaps/capivaraos-white.png %{buildroot}%{_datadir}/pixmaps/capivaraos-white.png
install -m 0644 build/pixmaps-med/capivaraos-logo-med.png %{buildroot}%{_datadir}/pixmaps/capivaraos-logo-med.png
install -m 0644 build/pixmaps-med/capivaraos-whitelogo-med.png %{buildroot}%{_datadir}/pixmaps/capivaraos-whitelogo-med.png

# ── Icones hicolor ───────────────────────────────────────────────────────────
for SIZE in 16 22 24 32 36 48 64 96 128 256 512; do
    install -d %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps
    install -m 0644 "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-logo.png" \
        %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/
    install -m 0644 "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-full-logo.png" \
        %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/
done

# ── Registro dos wallpapers no seletor de fundo do GNOME Settings ──────────
# Equivalente ao pacote de wallpaper KDE (metadata.json) da spin Marsh: um
# único XML em /usr/share/gnome-background-properties/ faz cada arquivo
# aparecer como opção no painel "Fundo" do GNOME Settings, com nome amigável
# (mesmo mecanismo usado pelo pacote gnome-backgrounds upstream).
install -d %{buildroot}%{_datadir}/gnome-background-properties
cat > %{buildroot}%{_datadir}/gnome-background-properties/capivaraos.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE wallpapers SYSTEM "gnome-wp-list.dtd">
<wallpapers>
  <wallpaper deleted="false">
    <name>CapivaraOS Azul</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-desktop.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Verde</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-desktop-verde.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Roxo</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-desktop-roxo.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Preto</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-desktop-preto.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Azul (logo branca)</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-desktop-azul-branco.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Verde (logo branca)</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-desktop-verde-branco.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Roxo (logo branca)</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-desktop-roxo-branco.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Ipê Rosa</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-desktop-foto-ipe.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Retrato</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-desktop-foto-capincho.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Taim</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-desktop-foto-taim.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Natação</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-desktop-foto-natacao.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Rio</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-desktop-foto-salto.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Iberá</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-desktop-foto-ibera.png</filename>
    <options>zoom</options>
  </wallpaper>
</wallpapers>
EOF

# ── Tema Plymouth (idêntico às demais spins, ver justificativa no spec da
# Marsh: inclui a tela "Instalando atualizações" com percentual) ───────────
install -d %{buildroot}%{_datadir}/plymouth/themes/capivaraos
install -m 0644 build/plymouth/logo.png \
    %{buildroot}%{_datadir}/plymouth/themes/capivaraos/logo.png

install -d %{buildroot}%{_datadir}/plymouth/themes/capivaraos/spinner
install -m 0644 build/plymouth/spinner/*.png \
    %{buildroot}%{_datadir}/plymouth/themes/capivaraos/spinner/

cat > %{buildroot}%{_datadir}/plymouth/themes/capivaraos/capivaraos.plymouth << 'EOF'
[Plymouth Theme]
Name=CapivaraOS
Description=CapivaraOS boot splash
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/capivaraos
ScriptFile=/usr/share/plymouth/themes/capivaraos/capivaraos.script
EOF

cat > %{buildroot}%{_datadir}/plymouth/themes/capivaraos/capivaraos.script << 'EOF'
Window.SetBackgroundTopColor(0.07, 0.09, 0.13);
Window.SetBackgroundBottomColor(0.07, 0.09, 0.13);

# ── Logo branca (acima do spinner) ──────────────────────────────────────────
logo.image = Image("logo.png");
logo.sprite = Sprite(logo.image);
logo.x = Window.GetWidth() / 2 - logo.image.GetWidth() / 2;
logo.y = Window.GetHeight() / 2 - logo.image.GetHeight() / 2 - 80;
logo.sprite.SetPosition(logo.x, logo.y, 1);

# ── Spinner (arco branco girando, logo abaixo da logo) ──────────────────────
spinner_frame_count = 30;
for (i = 0; i < spinner_frame_count; i++)
    spinner_image[i] = Image("spinner/" + i + ".png");

spinner.sprite = Sprite();
spinner.cx = Window.GetWidth() / 2;
spinner.cy = logo.y + logo.image.GetHeight() + 50;
spinner.frame = 0;

# ── Mensagem (abaixo do spinner) ────────────────────────────────────────────
# "updates"/"system-upgrade": modo usado pelo PackageKit/Software ao
# reiniciar para aplicar atualizacoes offline (systemd system-update.target).
is_updates = (Plymouth.GetMode() == "updates" || Plymouth.GetMode() == "system-upgrade");

if (Plymouth.GetMode() == "shutdown" || Plymouth.GetMode() == "reboot") {
    message_text = "Encerrando o CapivaraOS";
} else if (is_updates) {
    message_text = "Instalando atualizações";
} else {
    message_text = "Inicializando o CapivaraOS";
}

message.image = Image.Text(message_text, 1, 1, 1, 1, "Sans 14");
message.sprite = Sprite(message.image);
message.sprite.SetPosition(Window.GetWidth() / 2 - message.image.GetWidth() / 2,
                            spinner.cy + 70, 1);

# ── Aviso + percentual, somente durante atualizacao offline ────────────────
if (is_updates) {
    warning.image = Image.Text("Não desligue o computador", 0.8, 0.8, 0.8, 1, "Sans 11");
    warning.sprite = Sprite(warning.image);
    warning.sprite.SetPosition(Window.GetWidth() / 2 - warning.image.GetWidth() / 2,
                                spinner.cy + 95, 1);

    fun system_update_callback(progress) {
        percent.image = Image.Text(Math.Int(progress) + "%", 1, 1, 1, 1, "Sans 11");
        if (percent.sprite)
            percent.sprite.SetImage(percent.image);
        else
            percent.sprite = Sprite(percent.image);
        percent.sprite.SetPosition(Window.GetWidth() / 2 - percent.image.GetWidth() / 2,
                                    spinner.cy + 118, 1);
    }
    Plymouth.SetSystemUpdateFunction(system_update_callback);
}

fun refresh_callback() {
    spinner.frame++;
    if (spinner.frame >= spinner_frame_count * 3)
        spinner.frame = 0;
    idx = Math.Int(spinner.frame / 3);
    img = spinner_image[idx];
    spinner.sprite.SetImage(img);
    spinner.sprite.SetX(spinner.cx - img.GetWidth() / 2);
    spinner.sprite.SetY(spinner.cy - img.GetHeight() / 2);
}
Plymouth.SetRefreshFunction(refresh_callback);
EOF

# NOTA CapivaraOS: /etc/os-release/issue/issue.net NAO sao gerados aqui (em
# %{buildroot}). Pertencem a fedora-release-common; tê-los em %files causa
# conflito de arquivo no dnf. Escritos no sistema instalado em %posttrans.

# ── Avatar padrão (.face) para novos usuários ────────────────────────────────
install -d %{buildroot}%{_sysconfdir}/skel
install -m 0644 build/pixmaps/capivaraos-face.png %{buildroot}%{_sysconfdir}/skel/.face
ln -sf .face %{buildroot}%{_sysconfdir}/skel/.face.icon

# ── Branding do Cockpit (Anaconda WebUI) ────────────────────────────────────
install -d %{buildroot}%{_datadir}/cockpit/branding/capivaraos
install -m 0644 build/cockpit/logo.png %{buildroot}%{_datadir}/cockpit/branding/capivaraos/logo.png
install -m 0644 build/cockpit/logo.png %{buildroot}%{_datadir}/cockpit/branding/capivaraos/apple-touch-icon.png
install -m 0644 build/cockpit/favicon.ico %{buildroot}%{_datadir}/cockpit/branding/capivaraos/favicon.ico
cat > %{buildroot}%{_datadir}/cockpit/branding/capivaraos/branding.css << 'EOF'
/* SPDX-License-Identifier: LGPL-2.1-or-later */
#badge {
    inline-size: 225px;
    block-size: 80px;
    background-image: url("logo.png");
    background-size: contain;
    background-repeat: no-repeat;
}

#brand::before {
    content: "${NAME} <b>${VARIANT}</b>";
}

.anaconda {
    /* Paleta da marca CapivaraOS (verde) */
    --brand-default-light: #66bb6a;
    --brand-default: #2e7d32;
    --brand-default-dark: #1b5e20;

    .logo {
        background-image: url("logo.png");
        width: 2.5rem;
        height: 2.5rem;
    }
}

:not(.pf-v6-theme-dark) .anaconda {
    --pf-t--global--color--brand--default: var(--brand-default);
    --pf-t--global--color--brand--hover: var(--brand-default-dark);
}

.pf-v6-theme-dark .anaconda {
    --pf-t--global--color--brand--default: var(--brand-default-light);
    --pf-t--global--color--brand--hover: var(--brand-default);
}
EOF

# ── Decide de antemão o aviso de "repositórios de terceiros" do GNOME
# Software (fedora-third-party) ─────────────────────────────────────────────
# Sem isto, o diálogo "Habilitar repositórios de programas de terceiros?"
# reaparece para sempre na sessão live, mesmo clicando em "Ignorar" ou
# "Habilitar": ambos os botões disparam uma ação privilegiada via polkit
# (org.fedoraproject.thirdparty.run / .opt-out), que exige autenticação de
# admin -- e o "liveuser" da sessão live não tem senha definida para
# autenticar, então a ação falha silenciosamente e a decisão nunca é
# gravada em /var/lib/fedora-third-party/state.
#
# Em vez de tentar contornar isso com regras de polkit, pré-gravamos o
# estado já decidido como "não" -- coerente com a postura já adotada pelo
# CapivaraOS (ver PACKAGES.md da spin Marsh: "optamos por não habilitar RPM
# Fusion/repositórios de terceiros por padrão"). O arquivo não é
# %{_sysconfdir}/... mas sim /var/lib/ porque é onde o próprio
# fedora-third-party guarda esse estado (não é um arquivo de configuração
# do pacote fedora-third-party -- confirmado via "rpm -qf", ninguém é
# dono dele -- por isso podemos declará-lo nos %files deste pacote sem
# conflito). %config(noreplace): se o usuário mudar a escolha depois pelo
# GNOME Software (já autenticado normalmente, com senha real, no sistema
# instalado), uma atualização futura deste pacote não reverte a escolha.
install -d %{buildroot}%{_sharedstatedir}/fedora-third-party
cat > %{buildroot}%{_sharedstatedir}/fedora-third-party/state << 'EOF'
[main]
enabled = no
EOF

# ── Wallpaper padrão (system-wide, via dconf) ───────────────────────────────
# Mecanismo padrão do GNOME/dconf para definir um default que se aplica a
# qualquer usuário novo sem script de runtime: um keyfile em
# /etc/dconf/db/local.d/ + "dconf update" (feito em %posttrans) compilam o
# default na base binária /etc/dconf/db/local.d. Não bloqueamos a chave
# (sem locks/), então o usuário pode trocar livremente depois.
install -d %{buildroot}%{_sysconfdir}/dconf/db/local.d
cat > %{buildroot}%{_sysconfdir}/dconf/db/local.d/01-capivaraos-background << EOF
[org/gnome/desktop/background]
picture-uri='file://${DEFAULT_WP}'
picture-uri-dark='file://${DEFAULT_WP}'
picture-options='zoom'

[org/gnome/desktop/screensaver]
picture-uri='file://${DEFAULT_WP}'

[org/gnome/desktop/interface]
# Cor de destaque padrão (verde, cor da marca CapivaraOS). Chave nova do
# GNOME (47+) para o sistema de "Accent Colors" -- não bloqueamos a chave,
# o usuário pode trocar livremente em Configurações > Aparência.
accent-color='green'
EOF

# ── Wallpaper da tela de login (GDM) ─────────────────────────────────────────
# GDM roda sua própria sessão sob o usuário "gdm", que lê um perfil dconf
# PRÓPRIO (system-db:gdm), separado do perfil "user" usado por sessões
# normais. Sem isto, o greeter mostra o wallpaper padrão do Fedora/GNOME.
install -d %{buildroot}%{_sysconfdir}/dconf/profile
cat > %{buildroot}%{_sysconfdir}/dconf/profile/gdm << 'EOF'
user-db:user
system-db:gdm
EOF

install -d %{buildroot}%{_sysconfdir}/dconf/db/gdm.d
cat > %{buildroot}%{_sysconfdir}/dconf/db/gdm.d/01-capivaraos-background << EOF
[org/gnome/desktop/background]
picture-uri='file://${DEFAULT_WP}'
picture-uri-dark='file://${DEFAULT_WP}'
picture-options='zoom'
EOF

%post
# Splash de boot CapivaraOS
plymouth-set-default-theme capivaraos >/dev/null 2>&1 || true

# ── Sobrescreve o ícone "fedora-logo-icon" com a logo do CapivaraOS ────────
# A tela de boas-vindas da sessão live (gnome-initial-setup) e o painel
# "Sobre" do GNOME Settings NÃO lêem o LOGO= do /etc/os-release
# dinamicamente -- confirmado via "strings" no binário gnome-initial-setup:
# ele tem uma tabela FIXA, no código, de nomes de ícone por distro
# reconhecida ("fedora-logo-icon", "ubuntu-logo-icon", "opensuse-logo-icon"
# ...). Como "capivaraos" não está nessa tabela, cai no fallback Fedora.
# A correção (igual a outras distros baseadas em Fedora) é sobrescrever o
# CONTEÚDO do ícone "fedora-logo-icon" com a nossa logo, nos mesmos
# tamanhos em que o pacote fedora-logos o instala -- sem declarar esses
# caminhos em %files (evita conflito de arquivo no dnf, mesmo princípio
# usado para /etc/os-release).
for SIZE in 16 22 24 32 36 48 64 96 128 256 512; do
    SRC=%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-full-logo.png
    DST=%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/fedora-logo-icon.png
    [ -f "$SRC" ] && [ -d "$(dirname "$DST")" ] && cp -f "$SRC" "$DST"
done

# ── Sobrescreve logos hardcoded no gnome-control-center ───────────────────
# O painel "Sistema" (Sobre) do gnome-control-center no Fedora 44 usa caminhos
# FIXOS no código (cc-info-entry.c) para o logo da distro, independente do
# campo LOGO= do os-release. Os arquivos são do pacote fedora-logos:
# fedora_logo_med.png (279x80, colorido) e fedora_whitelogo_med.png (branco).
# Sobrescrevemos com nossa logo; sem declarar em %files (evita conflito com
# fedora-logos, mesmo padrão do fedora-logo-icon).
for PAIR in \
    "capivaraos-logo-med.png:fedora_logo_med.png" \
    "capivaraos-whitelogo-med.png:fedora_whitelogo_med.png"; do
    SRC=%{_datadir}/pixmaps/${PAIR%%:*}
    DST=%{_datadir}/pixmaps/${PAIR##*:}
    [ -f "$SRC" ] && [ -d "$(dirname "$DST")" ] && cp -f "$SRC" "$DST"
done

# GRUB_DISTRIBUTOR -> "CapivaraOS"
if [ -f %{_sysconfdir}/default/grub ]; then
    if grep -q '^GRUB_DISTRIBUTOR=' %{_sysconfdir}/default/grub; then
        sed -i 's/^GRUB_DISTRIBUTOR=.*/GRUB_DISTRIBUTOR="CapivaraOS"/' %{_sysconfdir}/default/grub
    else
        echo 'GRUB_DISTRIBUTOR="CapivaraOS"' >> %{_sysconfdir}/default/grub
    fi
fi

# Compila os keyfiles de /etc/dconf/db/*.d/ nas bases binarias lidas em
# tempo de execucao pelo gnome-shell/gdm.
dconf update >/dev/null 2>&1 || true

gtk-update-icon-cache -f %{_datadir}/icons/hicolor >/dev/null 2>&1 || true

%postun
if [ "$1" -eq 0 ]; then
    gtk-update-icon-cache -f %{_datadir}/icons/hicolor >/dev/null 2>&1 || true
    dconf update >/dev/null 2>&1 || true
fi

%posttrans
# Tema padrao do Plymouth (boot/desligamento): ver justificativa detalhada
# no spec da spin Marsh (idêntica para esta spin).
install -d %{_sysconfdir}/plymouth
cat > %{_sysconfdir}/plymouth/plymouthd.conf << 'EOF'
[Daemon]
Theme=capivaraos
EOF
plymouth-set-default-theme capivaraos >/dev/null 2>&1 || true

# /etc/os-release, /etc/issue, /etc/issue.net (fedora-release-common):
# escritos aqui (em vez de %files) para evitar conflito de arquivo no dnf.
cat > %{_sysconfdir}/os-release << 'EOF'
NAME="CapivaraOS"
VERSION="Snout 1.0.7"
RELEASE_TYPE=stable
ID=capivaraos
ID_LIKE=fedora
VERSION_ID=44
VERSION_CODENAME=snout
PLATFORM_ID="platform:f44"
PRETTY_NAME="CapivaraOS Snout 1.0.7"
ANSI_COLOR="0;32"
LOGO=capivaraos-full-logo
CPE_NAME="cpe:/o:capivaraos:capivaraos:44"
DEFAULT_HOSTNAME=capivaraos
HOME_URL="https://capivaraos.org"
DOCUMENTATION_URL="https://capivaraos.org"
SUPPORT_URL="https://capivaraos.org"
BUG_REPORT_URL="https://capivaraos.org"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=44
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=44
VARIANT="Snout 1.0.7"
VARIANT_ID=snout
EOF

cat > %{_sysconfdir}/issue << 'EOF'
CapivaraOS Snout 1.0.7 \n \l

EOF

cat > %{_sysconfdir}/issue.net << 'EOF'
CapivaraOS Snout 1.0.7
EOF

# ── Reaplica os-release apos qualquer atualizacao futura do sistema ────────
# Ver justificativa detalhada no spec da spin KDE (mesmo mecanismo: garante
# que o titulo GRUB/BLS de kernels novos nao volte a "Fedora Linux").
%transfiletriggerin -- %{_sysconfdir}/os-release
cat > %{_sysconfdir}/os-release << 'EOF'
NAME="CapivaraOS"
VERSION="Snout 1.0.7"
RELEASE_TYPE=stable
ID=capivaraos
ID_LIKE=fedora
VERSION_ID=44
VERSION_CODENAME=snout
PLATFORM_ID="platform:f44"
PRETTY_NAME="CapivaraOS Snout 1.0.7"
ANSI_COLOR="0;32"
LOGO=capivaraos-full-logo
CPE_NAME="cpe:/o:capivaraos:capivaraos:44"
DEFAULT_HOSTNAME=capivaraos
HOME_URL="https://capivaraos.org"
DOCUMENTATION_URL="https://capivaraos.org"
SUPPORT_URL="https://capivaraos.org"
BUG_REPORT_URL="https://capivaraos.org"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=44
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=44
VARIANT="Snout 1.0.7"
VARIANT_ID=snout
EOF

cat > %{_sysconfdir}/issue << 'EOF'
CapivaraOS Snout 1.0.7 \n \l

EOF

cat > %{_sysconfdir}/issue.net << 'EOF'
CapivaraOS Snout 1.0.7
EOF

for kver in $(ls /lib/modules 2>/dev/null); do
    [ -f "/lib/modules/${kver}/vmlinuz" ] && \
        kernel-install add "${kver}" "/lib/modules/${kver}/vmlinuz" >/dev/null 2>&1 || true
done

# ── Reaplica o ícone fedora-logo-icon após qualquer atualização futura ─────
# Mesmo mecanismo do file trigger de /etc/os-release: se uma atualização
# futura do fedora-logos reescrever algum desses arquivos, este trigger
# reaplica a nossa logo por cima.
%transfiletriggerin -- %{_datadir}/icons/hicolor/16x16/apps/fedora-logo-icon.png %{_datadir}/icons/hicolor/22x22/apps/fedora-logo-icon.png %{_datadir}/icons/hicolor/24x24/apps/fedora-logo-icon.png %{_datadir}/icons/hicolor/32x32/apps/fedora-logo-icon.png %{_datadir}/icons/hicolor/36x36/apps/fedora-logo-icon.png %{_datadir}/icons/hicolor/48x48/apps/fedora-logo-icon.png %{_datadir}/icons/hicolor/64x64/apps/fedora-logo-icon.png %{_datadir}/icons/hicolor/96x96/apps/fedora-logo-icon.png %{_datadir}/icons/hicolor/128x128/apps/fedora-logo-icon.png %{_datadir}/icons/hicolor/256x256/apps/fedora-logo-icon.png %{_datadir}/icons/hicolor/512x512/apps/fedora-logo-icon.png
for SIZE in 16 22 24 32 36 48 64 96 128 256 512; do
    SRC=%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-full-logo.png
    DST=%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/fedora-logo-icon.png
    [ -f "$SRC" ] && [ -d "$(dirname "$DST")" ] && cp -f "$SRC" "$DST"
done
gtk-update-icon-cache -f %{_datadir}/icons/hicolor >/dev/null 2>&1 || true

# ── Reaplica o logo do gnome-control-center após atualização do fedora-logos ─
%transfiletriggerin -- %{_datadir}/pixmaps/fedora_logo_med.png %{_datadir}/pixmaps/fedora_whitelogo_med.png
for PAIR in \
    "capivaraos-logo-med.png:fedora_logo_med.png" \
    "capivaraos-whitelogo-med.png:fedora_whitelogo_med.png"; do
    SRC=%{_datadir}/pixmaps/${PAIR%%:*}
    DST=%{_datadir}/pixmaps/${PAIR##*:}
    [ -f "$SRC" ] && [ -d "$(dirname "$DST")" ] && cp -f "$SRC" "$DST"
done

%files
%license backgrounds/CREDITOS.txt
%{_datadir}/backgrounds/capivaraos/
%{_datadir}/pixmaps/capivaraos.png
%{_datadir}/pixmaps/capivaraos-logo.png
%{_datadir}/pixmaps/capivaraos-white.png
%{_datadir}/pixmaps/capivaraos-logo-med.png
%{_datadir}/pixmaps/capivaraos-whitelogo-med.png
%{_datadir}/icons/hicolor/*/apps/capivaraos-logo.png
%{_datadir}/icons/hicolor/*/apps/capivaraos-full-logo.png
%{_datadir}/gnome-background-properties/capivaraos.xml
%{_datadir}/plymouth/themes/capivaraos/
%{_datadir}/cockpit/branding/capivaraos/
%{_sysconfdir}/skel/.face
%{_sysconfdir}/skel/.face.icon
%config(noreplace) %{_sharedstatedir}/fedora-third-party/state
%config(noreplace) %{_sysconfdir}/dconf/db/local.d/01-capivaraos-background
%config(noreplace) %{_sysconfdir}/dconf/profile/gdm
%config(noreplace) %{_sysconfdir}/dconf/db/gdm.d/01-capivaraos-background

%changelog
* Fri Jun 26 2026 CapivaraOS Project <hello@capivaraos.org> - 1.0.7-1
- Substitui a abordagem de extensão de fotos (que gerava borda artificial
  visível) por um recorte 4:3 nativo das imagens originais de alta resolução
  (Wikimedia Commons, 3:2, 4000–5565px de altura). As 6 fotos são recortadas
  centradas para 4:3, escaladas para 1920×1440 e têm logo+créditos inseridos
  no canto inferior direito. Remove a seção §6 do %build (não há mais
  extensão por espelho/blur); fotos já chegam como PNGs 1920×1440 na source.

* Fri Jun 26 2026 CapivaraOS Project <hello@capivaraos.org> - 1.0.6-1
- Corrige créditos CC BY-SA cortados e texto invertido abaixo da logo (BUG-27):
  a extensão 3:2 (1.0.5) cortava ~64px de cada lateral em telas 4:3, ocultando
  os créditos no canto esquerdo. O espelho invertia a zona do logo CapivaraOS
  (~y=990-1075), gerando texto de cabeça para baixo. Nova abordagem: 4:3
  (1920×1440), espelho nos 180px do topo (join perfeito) e fill suave amostrado
  de y≈900 no rodapé (acima da zona do logo), sem texto invertido nem borrão
  visível.

* Fri Jun 26 2026 CapivaraOS Project <hello@capivaraos.org> - 1.0.5-1
- Substitui extensão por blur (1.0.4) por espelho de reflexão: os primeiros e
  últimos 100px de cada foto são invertidos (-flip) e usados como extensão. O
  join é matematicamente perfeito (mesma linha da foto na costura), sem borrão
  visível no seletor de fundos ou na área de trabalho.
- Altera proporção alvo de 4:3 (1920×1440) para 3:2 (1920×1280), correspondendo
  à resolução exata do VM de testes (1024×682). Em monitores 16:9, o zoom recorta
  apenas os 100px espelhados de cada extremidade, preservando o conteúdo original.

* Fri Jun 26 2026 CapivaraOS Project <hello@capivaraos.org> - 1.0.4-1
- Corrige fotos com barras pretas em cima e embaixo (regressão do 1.0.3): a
  abordagem 'scaled' escondia os créditos mas criava barras visíveis. Nova
  solução: estende cada foto 16:9 (1920x1080) para 4:3 (1920x1440) adicionando
  180px de borda borrada no topo e rodapé. Com 'zoom' em telas 4:3 (VMs), encaixa
  perfeitamente sem barras; em 16:9, o zoom recorta apenas a zona borrada das
  extremidades, mantendo o conteúdo original (e créditos CC BY-SA) visível.
- Reverte picture-options de foto de 'scaled' de volta para 'zoom' (agora seguro
  com as fotos estendidas para 4:3).

* Fri Jun 26 2026 CapivaraOS Project <hello@capivaraos.org> - 1.0.3-1
- Dobra o tamanho da logo no painel "Sistema" (Sobre): substitui fedora_logo_med.png
  com imagem 192x192 (preenchimento total do AdwClamp) em vez de 279x80, fazendo
  a logo aparecer 2.4x maior verticalmente no painel.
- Corrige créditos das fotos de capivara cortados pelo modo zoom: fotos 1920x1080
  (16:9) em telas 4:3 sofriam crop de ~170px nas laterais, ocultando os créditos
  CC BY-SA no canto inferior esquerdo. Muda picture-options de zoom para scaled
  nos wallpapers de foto; wallpapers artísticos (sem créditos) continuam em zoom.
- Muda o wallpaper padrão para capivaraos-desktop.png (arte digital, sem créditos
  de terceiros) para melhor experiência visual em modo zoom no desktop padrão.

* Fri Jun 26 2026 CapivaraOS Project <hello@capivaraos.org> - 1.0.2-1
- Corrige logo no painel "Sistema" (Sobre) do gnome-control-center: o Fedora
  44 patcha o gnome-control-center para carregar o logo a partir de caminhos
  FIXOS no codigo (cc-info-entry.c) --  fedora_logo_med.png e
  fedora_whitelogo_med.png (279x80 px) -- ignorando o campo LOGO= do
  os-release. Sobrescrevemos esses arquivos com a logo CapivaraOS, com
  %transfiletriggerin para sobreviver a updates futuros do fedora-logos.
- Define PRETTY_NAME="CapivaraOS Snout 1.0.2" (versao completa no os-release).

* Thu Jun 25 2026 CapivaraOS Project <hello@capivaraos.org> - 1.0.1-1
- Corrige o dialogo "Habilitar repositorios de programas de terceiros?" do
  GNOME Software reaparecendo indefinidamente na sessao live: tanto
  "Ignorar" quanto "Habilitar" disparam uma acao privilegiada via polkit
  que exige autenticacao de admin, e o liveuser nao tem senha para
  autenticar -- a decisao nunca era gravada. Pre-gravamos o estado em
  /var/lib/fedora-third-party/state como "nao", coerente com a postura
  do CapivaraOS de nao habilitar repositorios de terceiros por padrao.

* Thu Jun 25 2026 CapivaraOS Project <hello@capivaraos.org> - 1.0.0-2
- Corrige logo do Fedora na tela de boas-vindas (gnome-initial-setup) e no
  painel "Sobre" do GNOME Settings: essas telas usam uma tabela fixa, no
  codigo, de nomes de icone por distro reconhecida (fedora-logo-icon,
  ubuntu-logo-icon, opensuse-logo-icon), nao o LOGO= do os-release.
  Sobrescrevemos o conteudo de fedora-logo-icon com a logo do CapivaraOS
  (com file trigger para sobreviver a updates futuros do fedora-logos)
- Define accent-color=green (verde, cor da marca) como padrao via dconf
- Adiciona tamanho de icone 36x36 (usado pelo fedora-logo-icon)

* Thu Jun 25 2026 CapivaraOS Project <hello@capivaraos.org> - 1.0.0-1
- Versao inicial do CapivaraOS Snout (Fedora 44, GNOME)
