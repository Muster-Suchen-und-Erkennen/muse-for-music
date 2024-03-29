"""Major refactor

Revision ID: 638ae6935168
Revises: 563a2aa9584c
Create Date: 2019-02-20 11:51:20.657900

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '638ae6935168'
down_revision = '563a2aa9584c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ambitus_group',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('highest_pitch_id', sa.Integer(), nullable=True),
        sa.Column('highest_octave_id', sa.Integer(), nullable=True),
        sa.Column('lowest_pitch_id', sa.Integer(), nullable=True),
        sa.Column('lowest_octave_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['highest_octave_id'], ['oktave.id'], name=op.f('fk_ambitus_group_highest_octave_id_oktave')),
        sa.ForeignKeyConstraint(['highest_pitch_id'], ['grundton.id'], name=op.f('fk_ambitus_group_highest_pitch_id_grundton')),
        sa.ForeignKeyConstraint(['lowest_octave_id'], ['oktave.id'], name=op.f('fk_ambitus_group_lowest_octave_id_oktave')),
        sa.ForeignKeyConstraint(['lowest_pitch_id'], ['grundton.id'], name=op.f('fk_ambitus_group_lowest_pitch_id_grundton')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_ambitus_group'))
    )
    op.create_table('formale_funktion_to_part',
        sa.Column('part_id', sa.Integer(), nullable=False),
        sa.Column('formale_funktion_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['formale_funktion_id'], ['formale_funktion.id'], name=op.f('fk_formale_funktion_to_part_formale_funktion_id')),
        sa.ForeignKeyConstraint(['part_id'], ['part.id'], name=op.f('fk_formale_funktion_to_part_part_id_part')),
        sa.PrimaryKeyConstraint('part_id', 'formale_funktion_id', name=op.f('pk_formale_funktion_to_part'))
    )
    op.create_table('musikalische_wendung_to_voice',
        sa.Column('voice_id', sa.Integer(), nullable=False),
        sa.Column('musikalische_wendung_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['musikalische_wendung_id'], ['musikalische_wendung.id'], name=op.f('fk_musikalische_wendung_to_voice_musikalische_wendung_id')),
        sa.ForeignKeyConstraint(['voice_id'], ['voice.id'], name=op.f('fk_musikalische_wendung_to_voice_voice_id_voice')),
        sa.PrimaryKeyConstraint('voice_id', 'musikalische_wendung_id', name=op.f('pk_musikalische_wendung_to_voice'))
    )

    with op.batch_alter_table('citations', schema=None) as batch_op:
        batch_op.drop_column('is_foreign')

    with op.batch_alter_table('harmonics', schema=None) as batch_op:
        batch_op.drop_constraint('harmonics_ibfk_6', type_='foreignkey')
        batch_op.drop_constraint('harmonics_ibfk_5', type_='foreignkey')
        batch_op.drop_column('nr_of_melody_tones_per_harmony')
        batch_op.drop_column('harmonic_rhythm_is_static')
        batch_op.drop_column('harmonic_rhythm_follows_rule')
        batch_op.drop_column('melody_tones_in_melody_two_id')
        batch_op.drop_column('melody_tones_in_melody_one_id')

    with op.batch_alter_table('part', schema=None) as batch_op:
        batch_op.drop_constraint('part_ibfk_3', type_='foreignkey')
        batch_op.drop_column('form_id')

    with op.batch_alter_table('person', schema=None) as batch_op:
        batch_op.drop_index('ix_person_canonical_name')
        batch_op.drop_column('canonical_name')
        batch_op.alter_column('birth_date',
               existing_type=sa.DATE(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('death_date',
               existing_type=sa.DATE(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('nationality',
               existing_type=sa.VARCHAR(length=40),
               type_=sa.String(length=100),
               existing_nullable=True)

    with op.batch_alter_table('sequence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('exact_repetition', sa.Boolean(), nullable=True))

    with op.batch_alter_table('sub_part', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ambitus_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_tutti', sa.Boolean(), nullable=True))
        batch_op.drop_constraint('sub_part_ibfk_2', type_='foreignkey')
        batch_op.drop_constraint('sub_part_ibfk_9', type_='foreignkey')
        batch_op.drop_constraint('sub_part_ibfk_11', type_='foreignkey')
        batch_op.drop_constraint('sub_part_ibfk_4', type_='foreignkey')
        batch_op.drop_constraint('sub_part_ibfk_10', type_='foreignkey')
        batch_op.drop_constraint('sub_part_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('fk_sub_part_ambitus_id_ambitus_group'), 'ambitus_group', ['ambitus_id'], ['id'])
        batch_op.drop_column('rhythm_id')
        batch_op.drop_column('composition_id')
        batch_op.drop_column('form_id')
        batch_op.drop_column('rendition_id')
        batch_op.drop_column('citations_id')
        batch_op.drop_column('satz_id')
        batch_op.alter_column('label',
               existing_type=sa.VARCHAR(length=5),
               type_=sa.String(length=191),
               existing_nullable=False)

    with op.batch_alter_table('voice', schema=None) as batch_op:
        batch_op.add_column(sa.Column('citations_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('composition_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('rendition_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('rhythm_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('voice_ibfk_2', type_='foreignkey')
        batch_op.drop_constraint('voice_ibfk_5', type_='foreignkey')
        batch_op.drop_constraint('voice_ibfk_6', type_='foreignkey')
        batch_op.drop_constraint('voice_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('fk_voice_composition_id_composition'), 'composition', ['composition_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_voice_rhythm_id_rhythm'), 'rhythm', ['rhythm_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_voice_rendition_id_rendition'), 'rendition', ['rendition_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_voice_citations_id_citations'), 'citations', ['citations_id'], ['id'])
        batch_op.drop_column('highest_pitch_id')
        batch_op.drop_column('highest_octave_id')
        batch_op.drop_column('lowest_pitch_id')
        batch_op.drop_column('lowest_octave_id')
        batch_op.drop_column('cites_own_melody_later')
        batch_op.drop_column('contains_repetition_from_outside')
        batch_op.drop_column('is_symmetric')
        batch_op.drop_column('is_repetitive')

    op.drop_table('formale_funktion_to_form')
    op.drop_table('form')
    op.drop_table('musikalische_wendung_to_sub_part')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('voice', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_repetitive', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('is_symmetric', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('contains_repetition_from_outside', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('cites_own_melody_later', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('lowest_octave_id', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('lowest_pitch_id', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('highest_octave_id', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('highest_pitch_id', sa.INTEGER(), nullable=True))
        batch_op.drop_constraint(batch_op.f('fk_voice_citations_id_citations'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_voice_rendition_id_rendition'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_voice_rhythm_id_rhythm'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_voice_composition_id_composition'), type_='foreignkey')
        batch_op.create_foreign_key('voice_ibfk_1', 'oktave', ['highest_octave_id'], ['id'])
        batch_op.create_foreign_key('voice_ibfk_6', 'grundton', ['lowest_pitch_id'], ['id'])
        batch_op.create_foreign_key('voice_ibfk_5', 'oktave', ['lowest_octave_id'], ['id'])
        batch_op.create_foreign_key('voice_ibfk_2', 'grundton', ['highest_pitch_id'], ['id'])
        batch_op.drop_column('rhythm_id')
        batch_op.drop_column('rendition_id')
        batch_op.drop_column('composition_id')
        batch_op.drop_column('citations_id')

    with op.batch_alter_table('sub_part', schema=None) as batch_op:
        batch_op.add_column(sa.Column('satz_id', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('citations_id', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('rendition_id', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('form_id', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('composition_id', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('rhythm_id', sa.INTEGER(), nullable=True))
        batch_op.drop_constraint(batch_op.f('fk_sub_part_ambitus_id_ambitus_group'), type_='foreignkey')
        batch_op.create_foreign_key('sub_part_ibfk_1', 'citations', ['citations_id'], ['id'])
        batch_op.create_foreign_key('sub_part_ibfk_10', 'rhythm', ['rhythm_id'], ['id'])
        batch_op.create_foreign_key('sub_part_ibfk_4', 'form', ['form_id'], ['id'])
        batch_op.create_foreign_key('sub_part_ibfk_11', 'satz', ['satz_id'], ['id'])
        batch_op.create_foreign_key('sub_part_ibfk_9', 'rendition', ['rendition_id'], ['id'])
        batch_op.create_foreign_key('sub_part_ibfk_2', 'composition', ['composition_id'], ['id'])
        batch_op.drop_column('is_tutti')
        batch_op.drop_column('ambitus_id')
        batch_op.alter_column('label',
               existing_type=sa.String(length=191),
               type_=sa.VARCHAR(length=5),
               existing_nullable=False)

    with op.batch_alter_table('sequence', schema=None) as batch_op:
        batch_op.drop_column('exact_repetition')

    with op.batch_alter_table('person', schema=None) as batch_op:
        batch_op.add_column(sa.Column('canonical_name', sa.VARCHAR(length=191), nullable=True))
        batch_op.create_index('ix_person_canonical_name', ['canonical_name'], unique=False)
        batch_op.alter_column('nationality',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=40),
               existing_nullable=True)
        batch_op.alter_column('death_date',
               existing_type=sa.Integer(),
               type_=sa.DATE(),
               existing_nullable=True)
        batch_op.alter_column('birth_date',
               existing_type=sa.Integer(),
               type_=sa.DATE(),
               existing_nullable=True)

    with op.batch_alter_table('part', schema=None) as batch_op:
        batch_op.add_column(sa.Column('form_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key('part_ibfk_3', 'form', ['form_id'], ['id'])

    with op.batch_alter_table('harmonics', schema=None) as batch_op:
        batch_op.add_column(sa.Column('melody_tones_in_melody_one_id', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('melody_tones_in_melody_two_id', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('harmonic_rhythm_follows_rule', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('harmonic_rhythm_is_static', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('nr_of_melody_tones_per_harmony', sa.FLOAT(), nullable=True))
        batch_op.create_foreign_key('harmonics_ibfk_5', 'anzahl_melodietoene', ['melody_tones_in_melody_one_id'], ['id'])
        batch_op.create_foreign_key('harmonics_ibfk_6', 'anzahl_melodietoene', ['melody_tones_in_melody_two_id'], ['id'])

    with op.batch_alter_table('citations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_foreign', sa.BOOLEAN(), nullable=True))

    op.create_table('musikalische_wendung_to_sub_part',
    sa.Column('sub_part_id', sa.INTEGER(), nullable=False),
    sa.Column('musikalische_wendung_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['musikalische_wendung_id'], ['musikalische_wendung.id'], name='musikalische_wendung_to_sub_part_ibfk_1'),
    sa.ForeignKeyConstraint(['sub_part_id'], ['sub_part.id'], name='musikalische_wendung_to_sub_part_ibfk_2'),
    sa.PrimaryKeyConstraint('sub_part_id', 'musikalische_wendung_id', name='pk_musikalische_wendung_to_sub_part')
    )
    op.create_table('formale_funktion_to_form',
    sa.Column('form_id', sa.INTEGER(), nullable=False),
    sa.Column('formale_funktion_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['form_id'], ['form.id'], name='fk_formale_funktion_to_form_form_id_form'),
    sa.ForeignKeyConstraint(['formale_funktion_id'], ['formale_funktion.id'], name='fk_formale_funktion_to_form_formale_funktion_id_formale_funktion'),
    sa.PrimaryKeyConstraint('form_id', 'formale_funktion_id', name='pk_formale_funktion_to_form')
    )
    op.create_table('form',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('form_schema_id', sa.INTEGER(), nullable=True),
    sa.Column('contains_theme', sa.BOOLEAN(), nullable=True),
    sa.CheckConstraint('contains_theme IN (0, 1)'),
    sa.ForeignKeyConstraint(['form_schema_id'], ['formschema.id'], name='form_ibfk_1'),
    sa.PrimaryKeyConstraint('id', name='pk_form')
    )
    op.drop_table('musikalische_wendung_to_voice')
    op.drop_table('formale_funktion_to_part')
    op.drop_table('ambitus_group')
    # ### end Alembic commands ###
