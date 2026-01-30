export interface Currency {
  id: number;
  code: string;
  name: string;
}

export interface Rate {
  date: string;
  value: number;
  currency_code: string;
}

export interface MonthNode {
  monthName: string;
  monthIndex: number;
  rates: Rate[];
}

export interface QuarterNode {
  quarterName: string;
  months: MonthNode[];
}

export interface YearNode {
  year: number;
  quarters: QuarterNode[];
}