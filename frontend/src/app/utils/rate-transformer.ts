import { MonthNode, QuarterNode, Rate, YearNode } from '../models/rate.models';

const MONTH_NAMES = [
  'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
  'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'
];

export function transformRatesToTree(rates: Rate[]): YearNode[] {
  // Guard Clause: Jeśli rates jest null/undefined lub puste
  if (!rates || !Array.isArray(rates) || rates.length === 0) {
    console.warn('transformRatesToTree: Otrzymano pustą listę lub nieprawidłowe dane.', rates);
    return [];
  }

  // 1. Kopia i sortowanie
  const sortedRates = [...rates].sort((a, b) => {
    // Zabezpieczenie przed brakiem daty
    const dateA = a.date || '';
    const dateB = b.date || '';
    return dateA.localeCompare(dateB);
  });
  
  const tree: YearNode[] = [];

  for (const rate of sortedRates) {
    // Pomijamy rekordy bez daty
    if (!rate.date) continue;

    const dateObj = new Date(rate.date);
    const year = dateObj.getFullYear();
    const monthIndex = dateObj.getMonth();
    
    // Obsługa NaN (gdy data jest błędna)
    if (isNaN(year)) continue;
    
    const quarterIndex = Math.floor(monthIndex / 3); 
    const quarterName = `${toRoman(quarterIndex + 1)} Kwartał`;

    // A. Rok
    let yearNode = tree.find(y => y.year === year);
    if (!yearNode) {
      yearNode = { year: year, quarters: [] };
      tree.push(yearNode);
    }

    // B. Kwartał
    let quarterNode = yearNode.quarters.find(q => q.quarterName === quarterName);
    if (!quarterNode) {
      quarterNode = { quarterName: quarterName, months: [] };
      yearNode.quarters.push(quarterNode);
    }

    // C. Miesiąc
    let monthNode = quarterNode.months.find(m => m.monthIndex === monthIndex);
    if (!monthNode) {
      monthNode = { 
        monthName: MONTH_NAMES[monthIndex], 
        monthIndex: monthIndex, 
        rates: [] 
      };
      quarterNode.months.push(monthNode);
    }

    // D. Dzień
    monthNode.rates.push(rate);
  }

  return tree;
}

function toRoman(num: number): string {
  const romans = ['I', 'II', 'III', 'IV'];
  return romans[num - 1] || '';
}