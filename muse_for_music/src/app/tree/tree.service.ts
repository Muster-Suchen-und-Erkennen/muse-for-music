import { Injectable } from '@angular/core';

import { EXAMPLE_TREE } from './mock-tree';
import { TREE } from './mock-tree';

@Injectable()
export class TreeService {

  getTree(): TREE[] {
    return EXAMPLE_TREE;
  }

  constructor() { }

}
