export const disciplines = [
  "Boxing",
  "Muay Thai",
  "Kickboxing",
  "BJJ",
  "Wrestling",
  "Judo",
  "Karate",
  "Taekwondo",
  "MMA",
  "Other",
];
export const goals = [
  "Improve general fitness",
  "Learn MMA",
  "Develop MMA skills",
  "Improve boxing",
  "Improve Muay Thai",
  "Improve BJJ",
  "Improve wrestling",
  "Improve strength",
  "Improve conditioning",
  "Prepare for amateur competition under qualified supervision",
  "Pursue long-term competitive MMA development",
  "Build muscle",
  "Manage body weight sustainably",
];
export const labelMap: Record<string, string> = {
  physical: "Physical attributes",
  background: "Martial arts background",
  style: "Fighting style",
  stance: "Stance",
  weight_class: "Division reference",
};
export const fmt = (v: number | null | undefined, suffix = "") =>
  v == null ? "Not recorded" : `${Number(v.toFixed(1))}${suffix}`;
export const today = () => new Date().toLocaleDateString("en-CA");
