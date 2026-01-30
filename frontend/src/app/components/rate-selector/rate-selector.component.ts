import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RatesService } from '../../services/rates.service';
import { Currency } from '../../models/rate.models';

@Component({
  selector: 'app-rate-selector',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './rate-selector.component.html',
  styleUrl: './rate-selector.component.css'
})
export class RateSelectorComponent implements OnInit {
  // Emiter zdarzeń do rodzica: przesyła wybrane dane
  @Output() search = new EventEmitter<{ currencyCode: string, dateFrom: string, dateTo: string }>();

  form: FormGroup;
  currencies: Currency[] = [];
  isLoading = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private ratesService: RatesService
  ) {
    // Inicjalizacja formularza z walidatorami
    // Domyślne daty: dzisiaj i 7 dni temu
    const today = new Date().toISOString().split('T')[0];
    const lastWeek = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

    this.form = this.fb.group({
      currency: ['', Validators.required],
      dateFrom: [lastWeek, Validators.required],
      dateTo: [today, Validators.required]
    });
  }

  ngOnInit(): void {
    this.loadCurrencies();
  }

  // Pobranie listy walut do dropdowna
  loadCurrencies(): void {
    this.isLoading = true;
    this.ratesService.getCurrencies().subscribe({
      next: (data) => {
        this.currencies = data;
        this.isLoading = false;
        // Opcjonalnie: ustaw domyślnie pierwszą walutę (np. USD jeśli jest dostępna)
        if (data.length > 0) {
           // Znajdź USD lub weź pierwszą
           const defaultCurrency = data.find(c => c.code === 'USD') || data[0];
           this.form.patchValue({ currency: defaultCurrency.code });
        }
      },
      error: (err) => {
        this.errorMessage = 'Nie udało się pobrać listy walut.';
        this.isLoading = false;
        console.error(err);
      }
    });
  }

  // Getter sprawdzający logikę dat (cross-field validation)
  get isDateRangeValid(): boolean {
    const { dateFrom, dateTo } = this.form.value;
    return dateFrom && dateTo && dateFrom <= dateTo;
  }

  onSubmit(): void {
    if (this.form.valid && this.isDateRangeValid) {
      const { currency, dateFrom, dateTo } = this.form.value;
      // Emituj zdarzenie do rodzica
      this.search.emit({
        currencyCode: currency,
        dateFrom,
        dateTo
      });
    }
  }
}