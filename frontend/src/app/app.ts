import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet], // Tylko RouterOutlet jest tu potrzebny
  template: `<router-outlet></router-outlet>`, // Inline template dla prostoty
  styles: [`
    :host {
      display: block;
      padding: 20px;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
  `]
})
export class App {}