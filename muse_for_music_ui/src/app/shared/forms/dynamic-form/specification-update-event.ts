export interface SpecificationUpdateEvent {
  path: string;
  type?: "aa" | "aai";
  remove?: boolean;
  recursive?: boolean;
  affectsArrayMembers?: boolean;
}

