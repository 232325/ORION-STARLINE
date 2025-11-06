import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Shield, 
  CheckCircle, 
  Award, 
  FileText, 
  Building, 
  Calendar,
  ExternalLink,
  Download,
  AlertCircle,
  Clock,
  Globe,
  Hash
} from 'lucide-react';

export const CertificationPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<'assay' | 'storage' | 'audit' | 'legal'>('assay');

  // Mock certification data
  const certificationData = {
    tokenId: id,
    nftName: "1 oz Gold Bar",
    certificationId: "CERT-GOLD-001-2024",
    status: "verified",
    createdAt: "2024-01-15T10:30:00Z",
    
    assay: {
      laboratoryName: "Metal Testing Laboratory Inc.",
      certificateId: "ASSAY-MTL-2024-001",
      assayDate: "2024-01-10",
      metalType: "GOLD",
      weight: 31.1035,
      purity: 99.99,
      dimensions: { length: 32.7, width: 32.7, height: 2.87 },
      serialNumber: "GOLD-001-2024",
      digitalHash: "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
      accreditation: "ISO 17025",
      method: "Fire Assay + XRF Verification"
    },

    storage: {
      facilityName: "Brink's Global Services",
      facilityAddress: "123 Vault Street, New York, NY 10001",
      vaultNumber: "BR-001-A",
      storageStartDate: "2024-01-12",
      insuranceProvider: "Lloyd's of London",
      insurancePolicyNumber: "POL-2024-001",
      insuranceValue: 50000,
      facilitySignature: "0xfedcba0987654321fedcba0987654321fedcba09",
      securityLevel: "AAA",
      auditFrequency: "Monthly"
    },

    audits: [
      {
        auditId: "AUDIT-2024-001",
        auditorName: "Deloitte & Touche LLP",
        auditDate: "2024-01-20",
        auditType: "comprehensive",
        findings: "All storage protocols followed. Metal condition excellent.",
        complianceScore: 95.5,
        recommendations: ["Continue current storage protocols"]
      }
    ],

    legal: {
      amlCompliant: true,
      kycVerified: true,
      taxReporting: "compliant",
      jurisdiction: "Delaware, USA",
      legalEntity: "MetalNFT Holdings LLC",
      complianceScore: 98.2
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'verified': return 'text-green-400';
      case 'pending': return 'text-yellow-400';
      case 'rejected': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'verified': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'pending': return <Clock className="w-5 h-5 text-yellow-400" />;
      case 'rejected': return <AlertCircle className="w-5 h-5 text-red-400" />;
      default: return <Clock className="w-5 h-5 text-slate-400" />;
    }
  };

  const tabs = [
    { id: 'assay', label: 'Assay Sertifikat', icon: Award },
    { id: 'storage', label: 'Saqlash Sertifikat', icon: Building },
    { id: 'audit', label: 'Audit', icon: FileText },
    { id: 'legal', label: 'Huquqiy', icon: Shield }
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Sertifikat ma'lumotlari</h1>
            <p className="text-slate-400">{certificationData.nftName}</p>
          </div>
          <div className="flex items-center space-x-3">
            {getStatusIcon(certificationData.status)}
            <span className={`font-semibold capitalize ${getStatusColor(certificationData.status)}`}>
              {certificationData.status === 'verified' ? 'Tasdiqlangan' : 
               certificationData.status === 'pending' ? 'Kutilmoqda' : 'Rad etilgan'}
            </span>
          </div>
        </div>

        <div className="grid md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-white mb-1">{certificationData.certificationId}</div>
            <div className="text-slate-400 text-sm">Sertifikat raqami</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-white mb-1">{certificationData.assay.metalType}</div>
            <div className="text-slate-400 text-sm">Metall turi</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-white mb-1">{certificationData.assay.weight}g</div>
            <div className="text-slate-400 text-sm">Vazn</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-white mb-1">{certificationData.assay.purity}%</div>
            <div className="text-slate-400 text-sm">Tozalik</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-slate-800 rounded-xl border border-slate-700">
        <div className="flex border-b border-slate-700 overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-6 py-4 font-medium transition-colors whitespace-nowrap ${
                activeTab === tab.id 
                  ? 'text-yellow-400 border-b-2 border-yellow-400 bg-slate-700/50' 
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/30'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="p-6">
          {/* Assay Tab */}
          {activeTab === 'assay' && (
            <div className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-slate-700 rounded-lg p-6">
                  <h3 className="text-white font-semibold mb-4 flex items-center space-x-2">
                    <Award className="w-5 h-5 text-yellow-400" />
                    <span>Laboratory ma'lumotlari</span>
                  </h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Laboratoriya:</span>
                      <span className="text-white">{certificationData.assay.laboratoryName}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Sertifikat raqami:</span>
                      <span className="text-white">{certificationData.assay.certificateId}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Akreditatsiya:</span>
                      <span className="text-green-400">{certificationData.assay.accreditation}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Tekshirish sanasi:</span>
                      <span className="text-white">{new Date(certificationData.assay.assayDate).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-700 rounded-lg p-6">
                  <h3 className="text-white font-semibold mb-4">Texnik ma'lumotlar</h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Metall:</span>
                      <span className="text-yellow-400 font-semibold">{certificationData.assay.metalType}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Vazn:</span>
                      <span className="text-white">{certificationData.assay.weight} g</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Tozalik:</span>
                      <span className="text-white">{certificationData.assay.purity}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">O'lchamlari:</span>
                      <span className="text-white">
                        {certificationData.assay.dimensions.length} x {certificationData.assay.dimensions.width} x {certificationData.assay.dimensions.height} mm
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Serial raqam:</span>
                      <span className="text-white">{certificationData.assay.serialNumber}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Tekshirish usuli:</span>
                      <span className="text-white">{certificationData.assay.method}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-slate-700 rounded-lg p-6">
                <h3 className="text-white font-semibold mb-4 flex items-center space-x-2">
                  <Hash className="w-5 h-5 text-blue-400" />
                  <span>Digital imzolash</span>
                </h3>
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="text-sm">
                    <div className="text-slate-400 mb-2">Digital hash:</div>
                    <div className="text-green-400 font-mono text-xs break-all">
                      {certificationData.assay.digitalHash}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 mt-4">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span className="text-green-400 text-sm">Hash tasdiqlangan</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Storage Tab */}
          {activeTab === 'storage' && (
            <div className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-slate-700 rounded-lg p-6">
                  <h3 className="text-white font-semibold mb-4 flex items-center space-x-2">
                    <Building className="w-5 h-5 text-blue-400" />
                    <span>Saqlash ma'lumotlari</span>
                  </h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Facility:</span>
                      <span className="text-white">{certificationData.storage.facilityName}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Manzil:</span>
                      <span className="text-white">{certificationData.storage.facilityAddress}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Vault raqami:</span>
                      <span className="text-white">{certificationData.storage.vaultNumber}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Saqlash boshlanishi:</span>
                      <span className="text-white">{new Date(certificationData.storage.storageStartDate).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-700 rounded-lg p-6">
                  <h3 className="text-white font-semibold mb-4">Xavfsizlik va sug'urta</h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Xavfsizlik darajasi:</span>
                      <span className="text-green-400 font-semibold">{certificationData.storage.securityLevel}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Sug'urtalovchi:</span>
                      <span className="text-white">{certificationData.storage.insuranceProvider}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Polisa raqami:</span>
                      <span className="text-white">{certificationData.storage.insurancePolicyNumber}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Sug'urta qiymati:</span>
                      <span className="text-white">${certificationData.storage.insuranceValue.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Audit chastotasi:</span>
                      <span className="text-white">{certificationData.storage.auditFrequency}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-slate-700 rounded-lg p-6">
                <h3 className="text-white font-semibold mb-4">Facility imzolash</h3>
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="text-sm">
                    <div className="text-slate-400 mb-2">Facility imzolash hash:</div>
                    <div className="text-blue-400 font-mono text-xs break-all">
                      {certificationData.storage.facilitySignature}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 mt-4">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span className="text-green-400 text-sm">Facility imzolash tasdiqlangan</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Audit Tab */}
          {activeTab === 'audit' && (
            <div className="space-y-6">
              {certificationData.audits.map((audit, index) => (
                <div key={index} className="bg-slate-700 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-white font-semibold">Audit #{audit.auditId}</h3>
                    <div className="flex items-center space-x-2">
                      <div className="text-2xl font-bold text-green-400">{audit.complianceScore}</div>
                      <span className="text-slate-400">/100</span>
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-6 mb-4">
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Auditor:</span>
                        <span className="text-white">{audit.auditorName}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Audit sanasi:</span>
                        <span className="text-white">{new Date(audit.auditDate).toLocaleDateString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Audit turi:</span>
                        <span className="text-white capitalize">{audit.auditType}</span>
                      </div>
                    </div>
                  </div>

                  <div className="mb-4">
                    <h4 className="text-white font-semibold mb-2">Topilmalar:</h4>
                    <p className="text-slate-300 text-sm">{audit.findings}</p>
                  </div>

                  <div>
                    <h4 className="text-white font-semibold mb-2">Tavsiyalar:</h4>
                    <ul className="text-slate-300 text-sm space-y-1">
                      {audit.recommendations.map((rec, idx) => (
                        <li key={idx} className="flex items-start space-x-2">
                          <span className="text-yellow-400 mt-1">•</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Legal Tab */}
          {activeTab === 'legal' && (
            <div className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-slate-700 rounded-lg p-6">
                  <h3 className="text-white font-semibold mb-4 flex items-center space-x-2">
                    <Shield className="w-5 h-5 text-green-400" />
                    <span>Compliance</span>
                  </h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-400">AML:</span>
                      <div className="flex items-center space-x-1">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        <span className="text-green-400">Muvofiq</span>
                      </div>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">KYC:</span>
                      <div className="flex items-center space-x-1">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        <span className="text-green-400">Tasdiqlangan</span>
                      </div>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Soliq hisoboti:</span>
                      <div className="flex items-center space-x-1">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        <span className="text-green-400">Muvofiq</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-700 rounded-lg p-6">
                  <h3 className="text-white font-semibold mb-4">Huquqiy ma'lumotlar</h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Yurisdiksiya:</span>
                      <span className="text-white">{certificationData.legal.jurisdiction}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Yuridik shaxs:</span>
                      <span className="text-white">{certificationData.legal.legalEntity}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Compliance ball:</span>
                      <span className="text-green-400 font-semibold">{certificationData.legal.complianceScore}/100</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button className="flex items-center space-x-2 bg-slate-700 hover:bg-slate-600 text-white px-6 py-3 rounded-lg transition-colors">
          <Download className="w-4 h-4" />
          <span>Sertifikat yuklab olish</span>
        </button>
        <button className="flex items-center space-x-2 bg-slate-700 hover:bg-slate-600 text-white px-6 py-3 rounded-lg transition-colors">
          <ExternalLink className="w-4 h-4" />
          <span>Blockchain da ko'rish</span>
        </button>
        <Link 
          to={`/metal/${id}`}
          className="flex items-center space-x-2 bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-6 py-3 rounded-lg font-semibold hover:from-yellow-600 hover:to-orange-600 transition-colors"
        >
          <ExternalLink className="w-4 h-4" />
          <span>NFT ga o'tish</span>
        </Link>
      </div>
    </div>
  );
};