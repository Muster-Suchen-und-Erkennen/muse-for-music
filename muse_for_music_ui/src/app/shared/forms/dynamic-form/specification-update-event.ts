export interface SpecificationUpdateEvent {
  path: string;
  remove?: boolean;
  recursive?: boolean;
  affectsArrayMembers?: boolean;
}

