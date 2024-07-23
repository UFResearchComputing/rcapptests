# BEGIN
set -o errtrace
trap 'catch $?' ERR
catch() {
echo "apptests caught an error:"
if [ "$1" != "0" ]; then
    echo "Error code $1. Terminating!"
    exit $1
fi
}

modules="ml"
APPTESTS_OUT_DIR="APPTESTS_OUT"

for module in "$@"; do
modules+=" $module"
APPTESTS_OUT_DIR+="_$module"
done
module purge .

eval "$modules"
echo $modules
# END