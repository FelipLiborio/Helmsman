import http from "k6/http";
import { check, sleep } from "k6";

// Perfil de carga em estágios — exercita os diferentes grupos de regras do fuzzy:
//   idle → carga leve → carga real → pico → saturação → recuperação → scale down
export const options = {
  stages: [
    { duration: "15s", target: 60  },  // carga moderada  (regras 3-5)
    { duration: "20s", target: 260 },  // carga real      (regras 6-8)
    { duration: "20s", target: 550 },  // pico            (regras 9-11)
    { duration: "10s", target: 650 },  // saturação       (regras 12-13)
    { duration: "10s", target: 50  },  // recuperação     (regra 9)
  ],
  thresholds: {
    http_req_failed:   ["rate<0.05"],   // menos de 5% de erro
    http_req_duration: ["p(95)<2000"],  // 95% abaixo de 2s
  },
};

const BASE = "http://localhost:8080";
const HEADERS = { accept: "application/json" };

export default function () {
  const res = http.get(`${BASE}/usuarios`, { headers: HEADERS });

  check(res, {
    "status 2xx": (r) => r.status >= 200 && r.status < 300,
  });

  sleep(Math.random() * 0.5); // leve jitter para não bater tudo junto
}

// k6 run  tests/k6/load.js
