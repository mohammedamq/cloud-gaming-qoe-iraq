#!/usr/bin/env bash
# Controlled-impairment replay used in Section 4.7 (Linux kernel 6.8).
# Downlink shaping on an IFB device fed from the client-facing interface (eth0).
# Run as root. WAN = eth0, IFB = ifb0.
set -euo pipefail
WAN=${1:-eth0}; IFB=${2:-ifb0}

setup_ifb() {
  modprobe ifb numifbs=1 || true
  ip link set dev "$IFB" up
  tc qdisc add dev "$WAN" handle ffff: ingress
  tc filter add dev "$WAN" parent ffff: protocol ip u32 match u32 0 0 \
     action mirred egress redirect dev "$IFB"
}
clear_all() { tc qdisc del dev "$IFB" root 2>/dev/null || true
              tc qdisc del dev "$WAN" ingress 2>/dev/null || true; }

profile_A() {  # Onsite: RTT 1 ms, jitter SD 0.5 ms, no loss
  tc qdisc add dev "$IFB" root handle 1: htb default 10
  tc class add dev "$IFB" parent 1: classid 1:10 htb rate 1000mbit
  tc qdisc add dev "$IFB" parent 1:10 handle 10: \
     netem delay 0.5ms 0.5ms distribution normal limit 4000
}
profile_B() {  # Ramadi: RTT 10 ms, jitter SD 3 ms, no loss
  tc qdisc add dev "$IFB" root handle 1: htb default 10
  tc class add dev "$IFB" parent 1: classid 1:10 htb rate 200mbit
  tc qdisc add dev "$IFB" parent 1:10 handle 10: \
     netem delay 5ms 3ms distribution normal limit 4000
}
profile_C() {  # Sina'ah: RTT 8 ms, jitter SD 12 ms, ~1.0% bursty (Gilbert-Elliott) loss
  tc qdisc add dev "$IFB" root handle 1: htb default 10
  tc class add dev "$IFB" parent 1: classid 1:10 htb rate 60mbit
  tc qdisc add dev "$IFB" parent 1:10 handle 10: \
     netem delay 4ms 12ms distribution normal \
     loss gemodel 3.5% 50% 92% 0% limit 4000
  # gemodel p=3.5% (good->bad), r=50% (bad->good), 1-h=92% (loss in bad), 1-k=0% (loss in good)
  # => mean loss ~1.0%, mean burst ~2 packets
}

case "${3:-C}" in
  A) setup_ifb; profile_A ;;
  B) setup_ifb; profile_B ;;
  C) setup_ifb; profile_C ;;
  clear) clear_all ;;
  *) echo "usage: $0 <wan> <ifb> {A|B|C|clear}"; exit 1 ;;
esac
tc -s qdisc show dev "$IFB"
