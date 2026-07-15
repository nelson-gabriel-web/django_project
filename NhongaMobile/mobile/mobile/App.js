import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, Alert } from 'react-native';

export default function App() {
  return (
    <View style={styles.container}>
      <Image
        source={require('./assets/logo.png')}
        style={styles.logo}
        resizeMode="contain"
      />
      <Text style={styles.title}>🚀 Nhonga Mobile</Text>
      <Text style={styles.subtitle}>Conectando oportunidades</Text>
      
      <TouchableOpacity 
        style={styles.button}
        onPress={() => Alert.alert('✅ Sucesso!', 'A app está a funcionar!')}
      >
        <Text style={styles.buttonText}>Testar App</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0e1a',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  logo: {
    width: 150,
    height: 150,
    marginBottom: 10,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#c0c0c0',
    marginTop: 10,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.5)',
    marginTop: 5,
  },
  button: {
    backgroundColor: '#c0c0c0',
    padding: 14,
    borderRadius: 8,
    marginTop: 30,
    width: 200,
    alignItems: 'center',
  },
  buttonText: {
    color: '#1a1a2e',
    fontWeight: '600',
    fontSize: 16,
  },
});