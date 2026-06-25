# NÃO é uma cópia literal do fedora-workstation-common.ks do spin-kickstarts
# upstream — as fontes oficiais (pagure.io e forge.fedoraproject.org) estão
# atrás de proteção anti-bot (Anubis, desafio JavaScript) que bloqueia
# acesso automatizado, então este arquivo foi reconstruído.
#
# Em compensação, o grupo de pacotes abaixo NÃO é um palpite: foi conferido
# diretamente no comps.xml real do Fedora 44 (repos fedora+updates) nesta
# máquina de build, via "dnf group list --hidden" + inspeção do environment
# "workstation-product-environment" no comps-Everything.xml. Esse é
# literalmente o environment-group usado pela ISO oficial do Fedora
# Workstation (GNOME): já inclui Firefox, LibreOffice, multimídia, impressão
# e o ambiente GNOME completo (grouplist: base-graphical,
# container-management, core, desktop-accessibility, firefox, fonts,
# gnome-desktop, guest-desktop-agents, hardware-support, libreoffice,
# multimedia, networkmanager-submodules, printing, workstation-product) —
# por isso não precisamos adicionar manualmente @firefox/@libreoffice/etc.
# como a spin Marsh faz para o KDE (cujo env-group não inclui esses grupos).
#
# NOTA CapivaraOS: ajustar este arquivo se um build real expor algo que o
# comps não deixou claro (ex.: pacote opcional específico do GNOME SIG que
# só aparece em teste).

%packages
# install env-group to resolve RhBug:1891500 (mesmo motivo do "@^" usado
# pela spin Marsh para o KDE)
@^workstation-product-environment

%end
