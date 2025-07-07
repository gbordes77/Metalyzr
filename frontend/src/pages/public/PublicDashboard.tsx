import React, { useState, useEffect } from 'react';
// Placeholders for shadcn/ui components
const Card = ({ children, ...props }: any) => <div {...props} className="border rounded-lg shadow-sm">{children}</div>;
const CardHeader = ({ children, ...props }: any) => <div {...props} className="p-4 border-b">{children}</div>;
const CardTitle = ({ children, ...props }: any) => <h3 {...props} className="font-semibold text-lg">{children}</h3>;
const CardContent = ({ children, ...props }: any) => <div {...props} className="p-4">{children}</div>;
const Button = ({ children, ...props }: any) => <button {...props} className="bg-gray-800 text-white px-4 py-2 rounded">{children}</button>;
const Input = (props: any) => <input {...props} className="border p-2 rounded w-full" />;
const Select = ({ children, ...props }: any) => <select {...props} className="border p-2 rounded">{children}</select>;
const SelectContent = ({ children, ...props }: any) => <>{children}</>;
const SelectItem = ({ children, ...props }: any) => <option {...props}>{children}</option>;
const SelectTrigger = ({ children, ...props }: any) => <div>{children}</div>;
const SelectValue = (props: any) => <span {...props} />;
const Badge = ({ children, ...props }: any) => <span {...props} className="bg-gray-200 text-gray-800 px-2 py-1 rounded-full text-sm">{children}</span>;
const Tabs = ({ children, ...props }: any) => <div>{children}</div>;
const TabsContent = ({ children, ...props }: any) => <div>{children}</div>;
const TabsList = ({ children, ...props }: any) => <div className="flex border-b">{children}</div>;
const TabsTrigger = ({ children, ...props }: any) => <button {...props} className="px-4 py-2 -mb-px border-b-2 border-transparent hover:border-gray-800">{children}</button>;

import { Search, Filter, TrendingUp, TrendingDown, Calendar, Download, BarChart3, PieChart as PieChartIcon, Activity } from 'lucide-react';
import { PieChart as RechartsChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const PublicDashboard = () => {
  const [metagameData, setMetagameData] = useState<any[]>([]);
  const [selectedFormat, setSelectedFormat] = useState('standard');
  const [timeRange, setTimeRange] = useState('30d');
  const [searchTerm, setSearchTerm] = useState('');

  // Mock data pour démonstration
  useEffect(() => {
    setMetagameData([
      { name: 'Mono-Red Aggro', value: 24.5, trend: 'up', change: '+3.2%', color: '#ef4444' },
      { name: 'Azorius Control', value: 18.3, trend: 'down', change: '-1.5%', color: '#3b82f6' },
      { name: 'Golgari Midrange', value: 15.7, trend: 'stable', change: '+0.3%', color: '#16a34a' },
      { name: 'Esper Legends', value: 12.4, trend: 'up', change: '+5.1%', color: '#8b5cf6' },
      { name: 'Gruul Aggro', value: 9.8, trend: 'down', change: '-2.7%', color: '#dc2626' },
      { name: 'Others', value: 19.3, trend: 'stable', change: '0%', color: '#94a3b8' }
    ]);
  }, [selectedFormat, timeRange]);

  const MetagameOverview = () => (
    <div className="grid gap-6 md:grid-cols-2">
      {/* Graphique en camembert */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Répartition du Métagame</span>
            <Button>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <RechartsChart>
              <Pie
                data={metagameData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({name, value}: any) => `${name}: ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {metagameData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </RechartsChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Liste des archétypes */}
      <Card>
        <CardHeader>
          <CardTitle>Top Archétypes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {metagameData.filter(d => d.name !== 'Others').map((archetype, index) => (
              <div key={archetype.name} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-200 font-semibold">
                    {index + 1}
                  </div>
                  <div>
                    <h4 className="font-medium">{archetype.name}</h4>
                    <p className="text-sm text-gray-500">{archetype.value}% du méta</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {archetype.trend === 'up' ? (
                    <TrendingUp className="h-4 w-4 text-green-500" />
                  ) : archetype.trend === 'down' ? (
                    <TrendingDown className="h-4 w-4 text-red-500" />
                  ) : (
                    <Activity className="h-4 w-4 text-yellow-500" />
                  )}
                  <span className={`text-sm font-medium ${
                    archetype.trend === 'up' ? 'text-green-500' : 
                    archetype.trend === 'down' ? 'text-red-500' : 
                    'text-yellow-500'
                  }`}>
                    {archetype.change}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const TournamentResults = () => (
    <Card>
      <CardHeader>
        <CardTitle>Résultats Récents</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {[
            {
              name: "Regional Championship Lyon",
              date: "2025-01-06",
              winner: "Alexandre Martin",
              deck: "Mono-Red Aggro",
              players: 247
            },
            {
              name: "Magic Online Challenge",
              date: "2025-01-05",
              winner: "ProPlayer123",
              deck: "Azorius Control",
              players: 128
            },
            {
              name: "Store Championship Paris",
              date: "2025-01-04",
              winner: "Sophie Dubois",
              deck: "Esper Legends",
              players: 64
            }
          ].map(tournament => (
            <div key={tournament.name} className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-semibold">{tournament.name}</h4>
                  <p className="text-sm text-gray-500">{tournament.players} joueurs • {tournament.date}</p>
                </div>
                <Badge>{tournament.deck}</Badge>
              </div>
              <div className="mt-2">
                <p className="text-sm">
                  <span className="font-medium">Vainqueur:</span> {tournament.winner}
                </p>
              </div>
            </div>
          ))}
          
          <Button>
            Voir tous les tournois
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  const DeckExplorer = () => (
    <div className="space-y-6">
      {/* Barre de recherche */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
          <Input 
            placeholder="Rechercher un deck, joueur ou carte..." 
            className="pl-10"
            value={searchTerm}
            onChange={(e: any) => setSearchTerm(e.target.value)}
          />
        </div>
        <Button>
          <Filter className="h-4 w-4 mr-2" />
          Filtres avancés
        </Button>
      </div>

      {/* Grille de decks */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[
          {
            archetype: "Mono-Red Aggro",
            player: "Alexandre Martin",
            tournament: "Regional Championship",
            place: "1st",
            date: "2025-01-06"
          },
          {
            archetype: "Azorius Control",
            player: "ProPlayer123",
            tournament: "MTGO Challenge",
            place: "1st",
            date: "2025-01-05"
          },
          {
            archetype: "Golgari Midrange",
            player: "Marie Laurent",
            tournament: "Regional Championship",
            place: "2nd",
            date: "2025-01-06"
          }
        ].map(deck => (
          <Card key={`${deck.player}-${deck.date}`} className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardContent className="p-4">
              <div className="space-y-2">
                <div className="flex justify-between items-start">
                  <h4 className="font-semibold">{deck.archetype}</h4>
                  <Badge>{deck.place}</Badge>
                </div>
                <p className="text-sm text-gray-500">{deck.player}</p>
                <p className="text-xs text-gray-500">
                  {deck.tournament} • {deck.date}
                </p>
                <Button>
                  Voir la liste
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Metalyzr</h1>
        <p className="text-lg text-gray-600">
          Intelligence compétitive pour Magic: The Gathering
        </p>
      </div>

      {/* Contrôles globaux */}
      <div className="flex gap-4 mb-6">
        <Select value={selectedFormat} onChange={(e: any) => setSelectedFormat(e.target.value)} aria-label="Select Format">
          <SelectItem value="standard">Standard</SelectItem>
          <SelectItem value="modern">Modern</SelectItem>
          <SelectItem value="pioneer">Pioneer</SelectItem>
          <SelectItem value="legacy">Legacy</SelectItem>
          <SelectItem value="vintage">Vintage</SelectItem>
        </Select>

        <Select value={timeRange} onChange={(e: any) => setTimeRange(e.target.value)} aria-label="Select Time Range">
          <SelectItem value="7d">7 derniers jours</SelectItem>
          <SelectItem value="30d">30 derniers jours</SelectItem>
          <SelectItem value="90d">3 derniers mois</SelectItem>
          <SelectItem value="all">Toutes les données</SelectItem>
        </Select>

        <div className="ml-auto flex gap-2">
          <Button>
            <Calendar className="h-4 w-4 mr-2" />
            Calendrier
          </Button>
          <Button>
            <BarChart3 className="h-4 w-4 mr-2" />
            Analytics
          </Button>
        </div>
      </div>

      {/* Contenu principal */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Vue d'ensemble</TabsTrigger>
          <TabsTrigger value="tournaments">Tournois</TabsTrigger>
          <TabsTrigger value="decks">Explorer les Decks</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <MetagameOverview />
        </TabsContent>

        <TabsContent value="tournaments">
          <TournamentResults />
        </TabsContent>

        <TabsContent value="decks">
          <DeckExplorer />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PublicDashboard; 