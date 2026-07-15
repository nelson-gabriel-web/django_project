# Script para iniciar o Expo sem ADB
function expo-start {
    $env:EXPO_NO_ADB=1
    npx expo start
}

expo-start