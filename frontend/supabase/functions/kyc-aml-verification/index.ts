// KYC/AML Verification Edge Function
// Foydalanuvchi identifikatsiyasi va AML tekshiruvlari

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.3';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
};

interface KYCSubmission {
  user_id: string;
  full_name: string;
  date_of_birth: string;
  nationality: string;
  address: string;
  document_type: 'passport' | 'id_card' | 'drivers_license';
  document_number: string;
  document_front_url: string;
  document_back_url?: string;
  selfie_url: string;
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const url = new URL(req.url);
    const action = url.searchParams.get('action');

    if (req.method === 'GET') {
      const userId = url.searchParams.get('user_id');
      
      if (!userId) {
        return new Response(
          JSON.stringify({ error: 'user_id majburiy' }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      // KYC statusini olish
      const { data: kycData, error: kycError } = await supabase
        .from('kyc_verification')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .limit(1)
        .single();

      // AML tekshiruvlarini olish
      const { data: amlData, error: amlError } = await supabase
        .from('aml_screening')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

      return new Response(
        JSON.stringify({
          kyc: kycData || null,
          aml_checks: amlData || [],
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // POST - KYC ma'lumotlarini yuborish
    const submission: KYCSubmission = await req.json();

    if (!submission.user_id || !submission.full_name || !submission.document_number) {
      return new Response(
        JSON.stringify({ error: 'Barcha majburiy maydonlarni to\'ldiring' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Hujjatlarni tekshirish
    const documentVerification = await verifyDocument(submission);
    
    // Yuz taqqoslash
    const faceMatch = await compareFaces(
      submission.document_front_url,
      submission.selfie_url
    );

    // AML screening
    const amlResults = await performAMLScreening(submission);

    // KYC ma'lumotlarini saqlash
    const verificationStatus = determineStatus(
      documentVerification,
      faceMatch,
      amlResults
    );

    const { data: kycRecord, error: kycError } = await supabase
      .from('kyc_verification')
      .insert({
        user_id: submission.user_id,
        full_name: submission.full_name,
        date_of_birth: submission.date_of_birth,
        nationality: submission.nationality,
        address: submission.address,
        document_type: submission.document_type,
        document_number: submission.document_number,
        document_front_url: submission.document_front_url,
        document_back_url: submission.document_back_url,
        selfie_url: submission.selfie_url,
        verification_status: verificationStatus,
        document_verified: documentVerification.isValid,
        face_match_score: faceMatch.score,
        aml_status: amlResults.status,
        risk_score: amlResults.riskScore,
        verified_at: verificationStatus === 'approved' ? new Date().toISOString() : null,
      })
      .select()
      .single();

    if (kycError) throw kycError;

    // AML natijalarini saqlash
    const { error: amlError } = await supabase
      .from('aml_screening')
      .insert({
        user_id: submission.user_id,
        screening_type: 'kyc_submission',
        risk_level: amlResults.riskLevel,
        sanctions_match: amlResults.sanctionsMatch,
        pep_match: amlResults.pepMatch,
        adverse_media: amlResults.adverseMedia,
        screening_results: amlResults.details,
        status: amlResults.status,
      });

    if (amlError) throw amlError;

    return new Response(
      JSON.stringify({
        success: true,
        kyc: kycRecord,
        verification: {
          document: documentVerification,
          faceMatch,
          aml: amlResults,
        },
        message: getStatusMessage(verificationStatus),
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('KYC/AML verification error:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

async function verifyDocument(submission: KYCSubmission) {
  // Hujjat tekshiruvi simulyatsiyasi
  // Real implementation: OCR, document authenticity checks
  
  const isValid = Math.random() > 0.1; // 90% success rate
  const confidence = Math.random() * 30 + 70; // 70-100%
  
  return {
    isValid,
    confidence,
    checks: {
      formatValid: true,
      notExpired: true,
      dataExtracted: true,
      securityFeatures: isValid,
    },
    extractedData: {
      name: submission.full_name,
      documentNumber: submission.document_number,
      dateOfBirth: submission.date_of_birth,
    },
  };
}

async function compareFaces(documentUrl: string, selfieUrl: string) {
  // Yuz taqqoslash simulyatsiyasi
  // Real implementation: Face recognition API
  
  const score = Math.random() * 30 + 70; // 70-100%
  const isMatch = score > 75;
  
  return {
    isMatch,
    score,
    confidence: Math.random() * 20 + 80,
  };
}

async function performAMLScreening(submission: KYCSubmission) {
  // AML screening simulyatsiyasi
  // Real implementation: Check against sanctions lists, PEP databases, adverse media
  
  const riskScore = Math.random() * 30; // 0-30
  const sanctionsMatch = Math.random() < 0.05; // 5% chance
  const pepMatch = Math.random() < 0.02; // 2% chance
  const adverseMedia = Math.random() < 0.03; // 3% chance
  
  let riskLevel = 'low';
  let status = 'clear';
  
  if (sanctionsMatch || pepMatch) {
    riskLevel = 'high';
    status = 'flagged';
  } else if (adverseMedia || riskScore > 20) {
    riskLevel = 'medium';
    status = 'review';
  }
  
  return {
    status,
    riskLevel,
    riskScore,
    sanctionsMatch,
    pepMatch,
    adverseMedia,
    details: {
      sanctionsLists: ['OFAC', 'UN', 'EU'],
      pepDatabases: ['WorldCheck', 'Dow Jones'],
      mediaSources: ['News API', 'Google News'],
      checksPerformed: 15,
      matchesFound: sanctionsMatch || pepMatch || adverseMedia ? 1 : 0,
    },
  };
}

function determineStatus(
  docVerification: any,
  faceMatch: any,
  amlResults: any
): string {
  if (!docVerification.isValid || !faceMatch.isMatch) {
    return 'rejected';
  }
  
  if (amlResults.status === 'flagged') {
    return 'rejected';
  }
  
  if (amlResults.status === 'review' || docVerification.confidence < 80) {
    return 'pending';
  }
  
  return 'approved';
}

function getStatusMessage(status: string): string {
  const messages: any = {
    approved: 'Tabriklaymiz! KYC tekshiruvi muvaffaqiyatli yakunlandi.',
    pending: 'Ma\'lumotlaringiz tekshirilmoqda. Bu 24-48 soat davom etishi mumkin.',
    rejected: 'KYC tekshiruvi rad etildi. Iltimos, to\'g\'ri ma\'lumotlar bilan qayta urinib ko\'ring.',
  };
  
  return messages[status] || 'Noma\'lum status';
}
