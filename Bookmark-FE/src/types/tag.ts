export interface Tag {
  id: string;
  name: string;
}

export interface ApiTag {
  id: string;
  name: string;
}

export interface TagCloudData {
  name: string;
  count: number;
}

export interface ITagCreateRequest {
  name: string;
}
