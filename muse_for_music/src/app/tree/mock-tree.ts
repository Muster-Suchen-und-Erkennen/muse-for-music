export class TREE {
    id: number;
    name: string;
    children?: TREE[];
}

export const EXAMPLE_TREE: TREE[] = [
    {
        id: 1,
        name: 'root1',
        children: [
        { id: 2, name: 'child1' },
        { id: 3, name: 'child2' }
        ]
    },
    {
        id: 4,
        name: 'root2',
        children: [
            { id: 5, name: 'child2.1' },
            {
                id: 6,
                name: 'child2.2',
                children: [
                { id: 7, name: 'subsub' }
                ]
            }
        ]
    }
];
