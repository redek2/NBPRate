import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RateSelectorComponent } from './rate-selector.component';
import { RatesService } from '../../services/rates.service';
import { of } from 'rxjs';
import { Currency } from '../../models/rate.models';

describe('RateSelectorComponent', () => {
  let component: RateSelectorComponent;
  let fixture: ComponentFixture<RateSelectorComponent>;
  let ratesServiceMock: jasmine.SpyObj<RatesService>;

  const dummyCurrencies: Currency[] = [
    { id: 1, code: 'USD', name: 'Dolar' },
    { id: 2, code: 'EUR', name: 'Euro' }
  ];

  beforeEach(async () => {
    // Tworzymy atrapę serwisu
    ratesServiceMock = jasmine.createSpyObj('RatesService', ['getCurrencies']);
    ratesServiceMock.getCurrencies.and.returnValue(of(dummyCurrencies));

    await TestBed.configureTestingModule({
      // Importujemy komponent (standalone), a nie deklarujemy
      imports: [RateSelectorComponent],
      providers: [
        { provide: RatesService, useValue: ratesServiceMock }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(RateSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges(); // Uruchamia ngOnInit
  });

  it('powinien się utworzyć i pobrać waluty przy starcie', () => {
    expect(component).toBeTruthy();
    expect(ratesServiceMock.getCurrencies).toHaveBeenCalled();
    expect(component.currencies.length).toBe(2);
    // Sprawdzamy czy ustawił domyślną walutę (USD z mocka)
    expect(component.form.get('currency')?.value).toBe('USD');
  });

  it('powinien oznaczyć formularz jako nieprawidłowy, gdy data OD > DO', () => {
    component.form.patchValue({
      dateFrom: '2024-02-01',
      dateTo: '2024-01-01' // Data wsteczna
    });
    
    expect(component.isDateRangeValid).toBeFalse();
  });

  it('powinien wyemitować zdarzenie search przy poprawnym submit', () => {
    spyOn(component.search, 'emit');

    component.form.patchValue({
      currency: 'EUR',
      dateFrom: '2024-01-01',
      dateTo: '2024-01-31'
    });

    component.onSubmit();

    expect(component.search.emit).toHaveBeenCalledWith({
      currencyCode: 'EUR',
      dateFrom: '2024-01-01',
      dateTo: '2024-01-31'
    });
  });
});