export type Player = {
  id: string;
  telegram_id: number;
  username: string | null;
  xp: number;
  xgen_balance: number;
  fragments_balance: number;
  daily_streak: number;
  ship_count: number;
  ship_id: string;
};

export type Ship = {
  id: string;
  player_id: string;
  name: string;
  tea_level: number;
  optimism: number;
  speed: number;
  defense: number;
  luck: number;
  equipment?: { artifacts: unknown[] };
};

export type Zone = {
  id: string;
  name: string;
  description: string;
  image_url: string;
  fuel_cost: number;
  optimism_risk: number;
  duration_seconds: number;
  loot_table: unknown[];
};

export type RegisterPlayerRequest = {
  telegram_id: number;
  username: string;
};

export type RegisterPlayerResponse = {
  player: Player;
};

export type DailyLoginResponse = {
  player: Player;
  streak: number;
  reward: {
    xgen?: number;
    fragments?: number;
  };
};
