git pull
chmod 775 /sys/class/gpio/export
chmod 775 /sys/class/gpio/unexport
git pull
for gpio in "65" "68" "70" "71" "72" "73" "74" "76"; do
    GPIO_DIR=$(ls /sys/class/gpio/ | grep ${gpio})
    if [ -n "$GPIO_DIR" ]; then
            echo "GPIO already exist from past error"
            echo ${gpio} > /sys/class/gpio/unexport
            sleep 1
    fi
    echo ${gpio} > /sys/class/gpio/export
    sleep 1
    echo "out" > /sys/class/gpio/gpio${gpio}/direction
done

for gpio in "111" "112" "113" "114" "117" "118" "75"; do
    GPIO_DIR=$(ls /sys/class/gpio/ | grep ${gpio})
    if [ -n "$GPIO_DIR" ]; then
            echo "GPIO already exist from past error"
            echo ${gpio} > /sys/class/gpio/unexport
            sleep 1
    fi
    echo ${gpio} > /sys/class/gpio/export
    sleep 1
    echo "in" > /sys/class/gpio/gpio${gpio}/direction
done