import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import { Currency, Rate } from '../models/rate.models';

@Injectable({
  providedIn: 'root'
})
export class RatesService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // 1. Pobranie listy walut
  getCurrencies(): Observable<Currency[]> {
    return this.http.get<Currency[]>(`${this.apiUrl}/currencies`)
      .pipe(
        catchError(this.handleError)
      );
  }

  // 2. Pobranie kursów historycznych
  getRates(currencyCode: string, dateFrom: string, dateTo: string): Observable<Rate[]> {
    // Budowanie URL: /rates/USD/2024-01-01/2024-01-31
    const url = `${this.apiUrl}/rates/${currencyCode}/${dateFrom}/${dateTo}`;
    return this.http.get<Rate[]>(url)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Centralna obsługa błędów HTTP (logika techniczna, nie prezentacyjna)
  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'Unknown error occurred';

    if (error.error instanceof ErrorEvent) {
      // Błąd po stronie klienta/sieci
      errorMessage = `Client Error: ${error.error.message}`;
    } else {
      // Błąd zwrócony przez Backend (404, 500, itp.)
      errorMessage = `Server Error: ${error.status} - ${error.message}`;
    }

    console.error(errorMessage);
    // Przekazanie błędu dalej do komponentu, aby mógł wyświetlić komunikat
    return throwError(() => new Error(errorMessage));
  }
}