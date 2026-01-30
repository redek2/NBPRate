import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { YearNode } from '../../models/rate.models';

@Component({
  selector: 'app-rate-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './rate-list.component.html',
  styleUrl: './rate-list.component.css'
})
export class RateListComponent {
  @Input() data: YearNode[] = [];
}