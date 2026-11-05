#!/usr/bin/env bash
# ShadowsocksR 与 ss-panel（旧项目，保持原有行为）。
#
# 用法（通过 vpn.sh 调用）：
#   vpn.sh ssr install      克隆 shadowsocksr，初始化配置，复制 ssr_conf/*.json
#   vpn.sh ssr sspanel      部署 ss-panel（需要 PHP 和 composer 环境）
#
# 路径可用环境变量改：SSR_WORKDIR（默认 ${WORKDIR}）、PANEL_WORKDIR（默认 /home/web/webroot）。

SSR_REPO="${SSR_REPO:-https://github.com/themass/shadowsocksr.git}"
PANEL_WORKDIR="${PANEL_WORKDIR:-/home/web/webroot}"

ssr_usage() {
    cat <<EOF
SSR 模块:
  install     克隆 shadowsocksr 到 \${SSR_WORKDIR:-${WORKDIR}}，初始化并复制 ssr_conf/*.json
  sspanel     部署 ss-panel 到 ${PANEL_WORKDIR}（配置取自 ss_panel/env）
EOF
}

ssr_install() {
    local dir="${SSR_WORKDIR:-$WORKDIR}"
    have git || ensure_cmds git
    mkdir -p "$dir"
    cd "$dir" || die "进入 ${dir} 失败"
    if [ -d shadowsocksr/.git ]; then
        log "shadowsocksr 已存在，拉取更新"
        git -C shadowsocksr pull --ff-only || warn "git pull 失败，沿用现有代码"
    else
        git clone "$SSR_REPO" || die "克隆 ${SSR_REPO} 失败"
    fi
    cd shadowsocksr || die "进入 shadowsocksr 失败"
    bash setup_cymysql.sh || die "setup_cymysql.sh 失败"
    bash initcfg.sh || die "initcfg.sh 失败"
    # 只复制 json 配置，ssr_conf 里的 ssr_proxy.md 是说明文档，不该进代码目录。
    local f
    for f in "${MYCONF_HOME}"/ssr_conf/*.json; do
        [ -f "$f" ] || continue
        install_file "$f" "./$(basename "$f")" 644
    done
    log "SSR 已部署: ${dir}/shadowsocksr（用户和端口在 user-config.json / usermysql.json 里配置）"
}

ssr_sspanel() {
    have php || die "需要先安装 PHP"
    have git || ensure_cmds git
    [ -f "${MYCONF_HOME}/ss_panel/env" ] || die "缺少 ${MYCONF_HOME}/ss_panel/env"
    mkdir -p "$PANEL_WORKDIR"
    cd "$PANEL_WORKDIR" || die "进入 ${PANEL_WORKDIR} 失败"
    rm -rf ss-panel
    git clone https://github.com/orvice/ss-panel.git -b master || die "克隆 ss-panel 失败"
    cd ss-panel || die "进入 ss-panel 失败"
    download "https://getcomposer.org/installer" composer-setup.php || die "下载 composer 安装器失败"
    php composer-setup.php && rm -f composer-setup.php
    php composer.phar install || die "composer install 失败"
    install_file "${MYCONF_HOME}/ss_panel/env" .env 600
    php xcat migrate || die "数据库迁移失败，检查 .env 里的数据库连接"
    # 面板要写 storage 目录。沿用原来的宽松权限，面板已是停止维护的旧项目，别暴露在公网。
    chmod -R 777 storage
    log "ss-panel 已部署: ${PANEL_WORKDIR}/ss-panel"
}

ssr_main() {
    local action="${1:-}"
    [ $# -gt 0 ] && shift
    case "$action" in
        install) ssr_install ;;
        sspanel) ssr_sspanel ;;
        '' | help | -h | --help) ssr_usage ;;
        *)
            err "未知动作: ${action}"
            ssr_usage
            return 2
            ;;
    esac
}
