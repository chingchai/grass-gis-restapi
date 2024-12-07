test -r /Users/chingchaih/.alias && source /Users/chingchaih/.alias
setopt PROMPT_SUBST
PS1='GRASS : %1~ > '
grass_prompt() {
    MAPSET_PATH="`g.gisenv get=GISDBASE,LOCATION_NAME,MAPSET separator='/'`"
    _GRASS_DB_PLACE="`g.gisenv get=LOCATION_NAME,MAPSET separator='/'`"
    
    local z_lo=`g.gisenv get=LOCATION_NAME`
    local z_ms=`g.gisenv get=MAPSET`
    ZLOC="Mapset <$z_ms> in <$z_lo>"
    if [ "$_grass_old_mapset" != "$MAPSET_PATH" ] ; then
        fc -A -I
        HISTFILE="$MAPSET_PATH/.zsh_history"
        fc -R
        _grass_old_mapset="$MAPSET_PATH"
    fi
    
    if test -f "$MAPSET_PATH/cell/MASK" && test -d "$MAPSET_PATH/grid3/RASTER3D_MASK" ; then
        echo "[2D and 3D raster MASKs present]"
    elif test -f "$MAPSET_PATH/cell/MASK" ; then
        echo "[Raster MASK present]"
    elif test -d "$MAPSET_PATH/grid3/RASTER3D_MASK" ; then
        echo "[3D raster MASK present]"
    fi
}
PROMPT_COMMAND=grass_prompt
precmd() { eval "$PROMPT_COMMAND" }
RPROMPT='${ZLOC}'
export HOME="/Users/chingchaih"
export PATH="/Applications/GRASS-8.4.app/Contents/Resources/bin:/Applications/GRASS-8.4.app/Contents/Resources/scripts:/Users/chingchaih/Library/GRASS/8.4/Addons/bin:/Users/chingchaih/Library/GRASS/8.4/Addons/scripts:/opt/homebrew/sbin:/Users/chingchaih/.nvm/versions/node/v22.4.1/bin:/opt/homebrew/bin:/Users/chingchaih/google-cloud-sdk/bin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin:/Applications/Visual Studio Code.app/Contents/Resources/app/bin:Unknown command: "bin"

To see a list of supported npm commands, run:
  npm help"
trap "exit" TERM
