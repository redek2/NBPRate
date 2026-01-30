import { Component, ChangeDetectorRef } from '@angular/core'; // <--- 1. Dodano ChangeDetectorRef
import { CommonModule } from '@angular/common';
import { finalize } from 'rxjs/operators'; 
import { RateSelectorComponent } from '../../components/rate-selector/rate-selector.component';
import { RateListComponent } from '../../components/rate-list/rate-list.component';
import { RatesService } from '../../services/rates.service';
import { transformRatesToTree } from '../../utils/rate-transformer';
import { YearNode, Rate } from '../../models/rate.models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RateSelectorComponent, RateListComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
  treeData: YearNode[] = [];
  isLoading = false;
  errorMessage = '';

  // 2. Wstrzykujemy ChangeDetectorRef w konstruktorze
  constructor(
    private ratesService: RatesService,
    private cdr: ChangeDetectorRef 
  ) {}

  onSearch(params: { currencyCode: string, dateFrom: string, dateTo: string }): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.treeData = [];

    console.log('--- Rozpoczynam pobieranie danych ---', params);

    this.ratesService.getRates(params.currencyCode, params.dateFrom, params.dateTo)
      .pipe(
        finalize(() => {
          this.isLoading = false;
          console.log('--- Zakończono proces (spinner stop) ---');
          
          // 3. KLUCZOWA ZMIANA: Wymuszamy sprawdzenie zmian w widoku
          this.cdr.detectChanges(); 
        })
      )
      .subscribe({
        next: (rates: Rate[]) => {
          console.log('Otrzymano dane z backendu:', rates);
          
          try {
            if (!Array.isArray(rates)) {
              throw new Error('Otrzymane dane nie są tablicą!');
            }
            this.treeData = transformRatesToTree(rates);
            console.log('Transformacja zakończona sukcesem:', this.treeData);
          } catch (e: any) {
            console.error('Błąd podczas transformacji danych:', e);
            this.errorMessage = 'Błąd przetwarzania danych: ' + e.message;
          }
        },
        error: (err) => {
          console.error('Błąd HTTP:', err);
          this.errorMessage = err.message || 'Wystąpił nieoczekiwany błąd serwera.';
        }
      });
  }
}