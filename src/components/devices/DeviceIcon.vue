<script setup>
import {
  AirVent,
  BatteryCharging,
  Cable,
  Coffee,
  CookingPot,
  Fan,
  Gamepad2,
  Heater,
  HousePlug,
  LampDesk,
  Lightbulb,
  Microwave,
  Monitor,
  PlugZap,
  Printer,
  Refrigerator,
  Router,
  Smartphone,
  Speaker,
  Tablet,
  Tv,
  WashingMachine,
} from 'lucide-vue-next'

const props = defineProps({
  icon: { type: String, default: 'plug' },
  size: { type: Number, default: 21 },
})

const icons = {
  air: AirVent,
  computer: Monitor,
  fridge: Refrigerator,
  washer: WashingMachine,
  microwave: Microwave,
  lamp: LampDesk,
  tv: Tv,
  fan: Fan,
  heater: Heater,
  router: Router,
  printer: Printer,
  phone: Smartphone,
  tablet: Tablet,
  speaker: Speaker,
  console: Gamepad2,
  coffee: Coffee,
  kitchen: CookingPot,
  bulb: Lightbulb,
  battery: BatteryCharging,
  cable: Cable,
  outlet: HousePlug,
  plug: PlugZap,
}
</script>

<template>
  <component :is="icons[props.icon] || PlugZap" :size="size" />
</template>
