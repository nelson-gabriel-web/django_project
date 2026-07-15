import React, { useEffect } from 'react';
import { View, Text, Image, StyleSheet, ActivityIndicator } from 'react-native';

const SplashScreen = ({ navigation }) => {
  useEffect(() => {
    // Aguarda 3 segundos e navega para o Login
    const timer = setTimeout(() => {
      navigation.replace('Login');
    }, 3000);

    // Limpar o timer quando o componente for desmontado
    return () => clearTimeout(timer);
  }, []);

  return (
    <View style={styles.container}>
      <Image
        source={require('../../assets/logo.png')}
        style={styles.logo}
        resizeMode="contain"
      />
      <Text style={styles.title}>Nhonga</Text>
      <Text style={styles.subtitle}>Conectando oportunidades</Text>
      <ActivityIndicator size="small" color="#c0c0c0" style={{ marginTop: 30 }} />
    </View>
  );
};

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
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#c0c0c0',
    marginTop: 10,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.4)',
    marginTop: 5,
  },
});

export default SplashScreen;