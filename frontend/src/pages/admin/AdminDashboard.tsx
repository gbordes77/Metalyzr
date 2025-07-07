import React, { useState, useEffect } from 'react';
import { PlusCircle, Save, Trash2, AlertCircle, CheckCircle, Search, Filter } from 'lucide-react';

// Placeholders for shadcn/ui components
const Card = ({ children, ...props }: any) => <div {...props} className="border rounded-lg shadow-sm">{children}</div>;
const CardHeader = ({ children, ...props }: any) => <div {...props} className="p-4 border-b">{children}</div>;
const CardTitle = ({ children, ...props }: any) => <h3 {...props} className="font-semibold text-lg">{children}</h3>;
const CardContent = ({ children, ...props }: any) => <div {...props} className="p-4">{children}</div>;
const Button = ({ children, ...props }: any) => <button {...props} className="bg-gray-800 text-white px-4 py-2 rounded">{children}</button>;
const Input = (props: any) => <input {...props} className="border p-2 rounded w-full" />;
const Label = ({ children, ...props }: any) => <label {...props} className="block mb-1 font-medium">{children}</label>;
const Select = ({ children, ...props }: any) => <select {...props} className="border p-2 rounded w-full">{children}</select>;
const SelectContent = ({ children, ...props }: any) => <>{children}</>;
const SelectItem = ({ children, ...props }: any) => <option {...props}>{children}</option>;
const SelectTrigger = ({ children, ...props }: any) => <div>{children}</div>;
const SelectValue = (props: any) => <span {...props} />;
const Badge = ({ children, ...props }: any) => <span {...props} className="bg-gray-200 text-gray-800 px-2 py-1 rounded-full text-sm">{children}</span>;
const Tabs = ({ children, ...props }: any) => <div>{children}</div>;
const TabsContent = ({ children, ...props }: any) => <div>{children}</div>;
const TabsList = ({ children, ...props }: any) => <div className="flex border-b">{children}</div>;
const TabsTrigger = ({ children, ...props }: any) => <button {...props} className="px-4 py-2 -mb-px border-b-2 border-transparent hover:border-gray-800">{children}</button>;

const AdminDashboard = () => {
  const [archetypes, setArchetypes] = useState<any[]>([]);
  const [selectedArchetype, setSelectedArchetype] = useState<any>(null);
  const [pendingDecks, setPendingDecks] = useState<any[]>([]);

  // Mock data pour démonstration
  useEffect(() => {
    setArchetypes([
      {
        id: 1,
        name: "Mono-Red Aggro",
        format: "Standard",
        category: "Aggro",
        confidence: 95,
        deckCount: 247,
        lastSeen: "2025-01-07",
      },
      {
        id: 2,
        name: "Azorius Control",
        format: "Standard",
        category: "Control",
        confidence: 88,
        deckCount: 189,
        lastSeen: "2025-01-07",
      }
    ]);

    setPendingDecks([
      {
        id: 101,
        player: "ProPlayer123",
        tournament: "Regional Championship",
        suggestedArchetype: "Mono-Red Aggro",
        confidence: 78,
      }
    ]);
  }, []);

  const ArchetypeManager = () => (
    <div className="space-y-6">
      {/* Barre de recherche et filtres */}
      <div className="flex gap-4 items-end">
        <div className="flex-1">
          <Label>Rechercher un archétype</Label>
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-400" />
            <Input placeholder="Nom, format, ou carte clé..." className="pl-8" />
          </div>
        </div>
        <Select aria-label="Filter by Format">
          <SelectTrigger>
            <SelectValue placeholder="Format" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous les formats</SelectItem>
            <SelectItem value="standard">Standard</SelectItem>
            <SelectItem value="modern">Modern</SelectItem>
          </SelectContent>
        </Select>
        <Button>
          <PlusCircle className="mr-2 h-4 w-4" />
          Nouvel Archétype
        </Button>
      </div>

      {/* Liste des archétypes */}
      <div className="grid gap-4">
        {archetypes.map(archetype => (
          <Card key={archetype.id} className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => setSelectedArchetype(archetype)}>
            <CardContent className="p-4">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-lg">{archetype.name}</h3>
                  <div className="flex gap-2 mt-1">
                    <Badge>{archetype.format}</Badge>
                    <Badge>{archetype.category}</Badge>
                    <Badge>
                      Confiance: {archetype.confidence}%
                    </Badge>
                  </div>
                </div>
                <div className="text-right text-sm text-gray-500">
                  <p>{archetype.deckCount} decks</p>
                  <p>Vu le {archetype.lastSeen}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );

  const RuleEditor = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Règles de Détection</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Type de règle</Label>
            <Select aria-label="Select Rule Type">
              <SelectTrigger>
                <SelectValue placeholder="Sélectionner un type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="contains_all">Contient toutes ces cartes</SelectItem>
                <SelectItem value="contains_any">Contient certaines de ces cartes</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button>
            <Save className="mr-2 h-4 w-4" />
            Enregistrer la règle
          </Button>
        </CardContent>
      </Card>
    </div>
  );

  const ValidationQueue = () => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Decks en attente de validation</h3>
      {pendingDecks.map(deck => (
        <Card key={deck.id}>
          <CardContent className="p-4">
            <div className="space-y-4">
              <p>Player: {deck.player}</p>
              <div className="flex gap-2">
                <Button>
                  <CheckCircle className="mr-2 h-4 w-4" />
                  Valider
                </Button>
                <Button>
                  <AlertCircle className="mr-2 h-4 w-4" />
                  Nouvel archétype
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Administration Metalyzr</h1>
      
      <Tabs defaultValue="archetypes" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="archetypes">Archétypes</TabsTrigger>
          <TabsTrigger value="validation">Validation</TabsTrigger>
          <TabsTrigger value="rules">Règles</TabsTrigger>
        </TabsList>

        <TabsContent value="archetypes">
          <ArchetypeManager />
        </TabsContent>

        <TabsContent value="validation">
          <ValidationQueue />
        </TabsContent>

        <TabsContent value="rules">
          <RuleEditor />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminDashboard; 