# NÃO é uma cópia literal do fedora-live-workstation.ks do spin-kickstarts
# upstream (ver nota em fedora-gnome-common.ks sobre o bloqueio de acesso
# às fontes oficiais). Estrutura espelhada do fedora-live-kde-base.ks da
# spin Marsh (mesma forma: inclui a base comum + o common da DE, e ajusta
# tema GTK do root + livesys_session).

# NOTA CapivaraOS: caminhos de %include são resolvidos pelo pykickstart
# relativos ao diretório de trabalho do processo anaconda (não ao diretório
# deste arquivo), por isso usamos "upstream/..." aqui — veja a observação em
# capivaraos-snout.ks e o cd para kickstart/ em build-all.sh.
%include upstream/fedora-live-base.ks
%include upstream/fedora-gnome-common.ks

%post

# set default GTK+ theme for root (mesmo padrao das outras spins; Adwaita ja
# vem com o GTK, nao precisa de pacote extra)
cat > /root/.gtkrc-2.0 << EOF
include "/usr/share/themes/Adwaita/gtk-2.0/gtkrc"
include "/etc/gtk-2.0/gtkrc"
gtk-theme-name="Adwaita"
EOF
mkdir -p /root/.config/gtk-3.0
cat > /root/.config/gtk-3.0/settings.ini << EOF
[Settings]
gtk-theme-name = Adwaita
EOF

# set livesys session type (usa o livesys-gnome de /usr/libexec/livesys/sessions.d/)
sed -i 's/^livesys_session=.*/livesys_session="gnome"/' /etc/sysconfig/livesys

%end
