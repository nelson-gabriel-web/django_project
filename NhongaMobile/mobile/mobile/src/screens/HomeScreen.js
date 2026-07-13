import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import { useAuth } from '../context/AuthContext';

const HomeScreen = ({ navigation }) => {
  const { user, logout } = useAuth();

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <View style={styles.header}>
          <Text style={styles.welcome}>Bem-vindo,</Text>
          <Text style={styles.name}>
            {user?.first_name || user?.username || 'Utilizador'}
          </Text>
        </View>

        <View style={styles.menuGrid}>
          <TouchableOpacity
            style={styles.menuCard}
            onPress={() => navigation.navigate('Requisicoes')}
          >
            <Text style={styles.menuIcon}>🔍</Text>
            <Text style={styles.menuLabel}>Buscar</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.menuCard}
            onPress={() => navigation.navigate('Perfil')}
          >
            <Text style={styles.menuIcon}>👤</Text>
            <Text style={styles.menuLabel}>Perfil</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.menuCard}
            onPress={() => navigation.navigate('Mapa')}
          >
            <Text style={styles.menuIcon}>🗺️</Text>
            <Text style={styles.menuLabel}>Mapa</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.menuCard}
            onPress={() => navigation.navigate('Transacoes')}
          >
            <Text style={styles.menuIcon}>💰</Text>
            <Text style={styles.menuLabel}>Transações</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>📌 Atividade Recente</Text>
          <Text style={styles.cardEmpty}>Nenhuma atividade recente</Text>
        </View>

        <TouchableOpacity style={styles.logoutButton} onPress={logout}>
          <Text style={styles.logoutText}>🔓 Sair</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0e1a',
  },
  header: {
    padding: 20,
    backgroundColor: 'rgba(255,255,255,0.03)',
    margin: 16,
    borderRadius: 12,
  },
  welcome: {
    color: 'rgba(255,255,255,0.5)',
    fontSize: 14,
  },
  name: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  menuGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 8,
    justifyContent: 'space-between',
  },
  menuCard: {
    width: '48%',
    backgroundColor: 'rgba(255,255,255,0.04)',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  menuIcon: {
    fontSize: 32,
  },
  menuLabel: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 14,
    marginTop: 8,
  },
  card: {
    backgroundColor: 'rgba(255,255,255,0.02)',
    margin: 16,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.04)',
  },
  cardTitle: {
    color: '#fff',
    fontSize: 16,
    marginBottom: 12,
  },
  cardEmpty: {
    color: 'rgba(255,255,255,0.2)',
    textAlign: 'center',
    padding: 20,
  },
  logoutButton: {
    backgroundColor: 'rgba(220,53,69,0.1)',
    margin: 16,
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(220,53,69,0.2)',
  },
  logoutText: {
    color: '#ff6b6b',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default HomeScreen;